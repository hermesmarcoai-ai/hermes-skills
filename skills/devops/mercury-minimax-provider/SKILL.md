---
name: mercury-minimax-provider
description: Add MiniMax as a native provider to Mercury Agent (cosmicstack-labs/mercury-agent)
---

# Mercury Agent — Add MiniMax Provider

Add MiniMax as a native provider to Mercury Agent (cosmicstack-labs/mercury-agent).

## Problem
Mercury doesn't ship with MiniMax support. MiniMax exposes an Anthropic-compatible endpoint (`https://api.minimax.io/anthropic`) but requires OpenAI-compatible SDK usage — `@ai-sdk/anthropic` doesn't work with custom base URLs.

## Files to Modify

### 1. Create `src/providers/minimax.ts`
```typescript
import { createOpenAI } from '@ai-sdk/openai';
import { generateText, streamText } from 'ai';
import { BaseProvider } from './base.js';
import type { ProviderConfig } from '../utils/config.js';
import type { LLMResponse, LLMStreamChunk } from './base.js';

export class MiniMaxProvider extends BaseProvider {
  readonly name = 'minimax';
  readonly model: string;
  private client: ReturnType<typeof createOpenAI>;
  private modelInstance: ReturnType<ReturnType<typeof createOpenAI>['languageModel']>;

  constructor(config: ProviderConfig) {
    super(config);
    this.model = config.model;

    this.client = createOpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseUrl || 'https://api.minimax.io/anthropic',
    });
    this.modelInstance = this.client(config.model);
  }

  async generateText(prompt: string, systemPrompt: string): Promise<LLMResponse> {
    const result = await generateText({
      model: this.modelInstance,
      system: systemPrompt,
      prompt,
    });

    return {
      text: result.text,
      inputTokens: result.usage?.promptTokens ?? 0,
      outputTokens: result.usage?.completionTokens ?? 0,
      totalTokens: (result.usage?.promptTokens ?? 0) + (result.usage?.completionTokens ?? 0),
      model: this.model,
      provider: this.name,
    };
  }

  async *streamText(prompt: string, systemPrompt: string): AsyncIterable<LLMStreamChunk> {
    const result = streamText({
      model: this.modelInstance,
      system: systemPrompt,
      prompt,
    });

    for await (const chunk of (await result).textStream) {
      yield { text: chunk, done: false };
    }
    yield { text: '', done: true };
  }

  isAvailable(): boolean {
    return this.config.apiKey.length > 0;
  }

  getModelInstance() {
    return this.modelInstance;
  }
}
```

### 2. `src/providers/index.ts` — add export
```typescript
export { MiniMaxProvider } from './minimax.js';
```

### 3. `src/providers/registry.ts`
- Add import: `import { MiniMaxProvider } from './minimax.js';`
- Add to `entries` array: `config.providers.minimax`
- Add case: `} else if (pc.name === 'minimax') { provider = new MiniMaxProvider(pc); }`

### 4. `src/utils/config.ts`
- Add to `ProviderName` type: `'minimax'`
- Add to `MercuryConfig.providers`: `minimax: ProviderConfig;`
- Add default config block:
```typescript
minimax: {
  name: 'minimax',
  apiKey: getEnv('MINIMAX_API_KEY', ''),
  baseUrl: getEnv('MINIMAX_BASE_URL', 'https://api.minimax.io/anthropic'),
  model: getEnv('MINIMAX_MODEL', 'MiniMax-M2.7-highspeed'),
  enabled: getEnvBool('MINIMAX_ENABLED', false),
},
```

## Build & Reinstall
```bash
npm run build
npm uninstall -g @cosmicstack/mercury-agent
npm install -g /path/to/mercury-agent
```

## Configure
Update `~/.mercury/mercury.yaml`:
```yaml
providers:
  default: minimax
  minimax:
    name: minimax
    apiKey: YOUR_MINIMAX_API_KEY
    baseUrl: https://api.minimax.io/anthropic
    model: MiniMax-M2.7-highspeed
    enabled: true
```

## Key Lesson
Use `createOpenAI` (not `createAnthropic`) for MiniMax — despite the endpoint being Anthropic-compatible, the SDK auth mechanism requires OpenAI-style client creation with baseURL override.
