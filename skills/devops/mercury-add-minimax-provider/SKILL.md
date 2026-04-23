---
name: mercury-add-minimax-provider
description: Add MiniMax as a provider to Mercury agent (MiniMax-M2.7-highspeed via Anthropic-compatible endpoint)
triggers:
  - add minimax to mercury
  - mercury provider minimax
  - mercury minimax setup
---

# Mercury — Add MiniMax Provider

## What this does
Adds MiniMax (model: `MiniMax-M2.7-highspeed`) as a provider to Mercury, using MiniMax's Anthropic-compatible API endpoint.

## Files to modify

### 1. Create `src/providers/minimax.ts`
```typescript
import { createAnthropic } from '@ai-sdk/anthropic';
import { generateText, streamText } from 'ai';
import { BaseProvider } from './base.js';
import type { ProviderConfig } from '../utils/config.js';
import type { LLMResponse, LLMStreamChunk } from './base.js';

export class MiniMaxProvider extends BaseProvider {
  readonly name = 'minimax';
  readonly model: string;
  private client: ReturnType<typeof createAnthropic>;
  private modelInstance: ReturnType<ReturnType<typeof createAnthropic>['languageModel']>;

  constructor(config: ProviderConfig) {
    super(config);
    this.model = config.model;
    // IMPORTANT: MiniMax uses Anthropic-compatible endpoint at /v1/messages
    this.client = createAnthropic({
      apiKey: config.apiKey,
      baseURL: config.baseUrl || 'https://api.minimax.io/anthropic/v1',
    });
    this.modelInstance = this.client(config.model);
  }

  async generateText(prompt: string, systemPrompt: string): Promise<LLMResponse> {
    const result = await generateText({
      model: this.modelInstance,
      system: systemPrompt,
      prompt,
    });

    let text = result.text;
    if (!text && result.raw && result.raw.content) {
      const content = result.raw.content;
      if (Array.isArray(content)) {
        const textBlocks = content.filter((c: any) => c.type === 'text' && c.text);
        text = textBlocks.map((c: any) => c.text).join('\n');
      }
    }

    return {
      text: text || '',
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

    for await (const chunk of (await result).fullStream) {
      if (chunk.type === 'text' || (chunk.type === 'assistant' && typeof chunk.content === 'string')) {
        yield { text: typeof chunk.content === 'string' ? chunk.content : '', done: false };
      }
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

### 2. Update `src/providers/index.ts`
Add export:
```typescript
export { MiniMaxProvider } from './minimax.js';
```

### 3. Update `src/providers/registry.ts`
Add import and case:
```typescript
import { MiniMaxProvider } from './minimax.js';
```
In constructor entries array:
```typescript
config.providers.minimax,
```
In provider instantiation:
```typescript
} else if (pc.name === 'minimax') {
  provider = new MiniMaxProvider(pc);
}
```

### 4. Update `src/utils/config.ts`
Add to `ProviderName` type:
```typescript
| 'minimax';
```
Add to `MercuryConfig.providers`:
```typescript
minimax: ProviderConfig;
```
Add default config:
```typescript
minimax: {
  name: 'minimax',
  apiKey: getEnv('MINIMAX_API_KEY', ''),
  baseUrl: getEnv('MINIMAX_BASE_URL', 'https://api.minimax.io/anthropic/v1'),
  model: getEnv('MINIMAX_MODEL', 'MiniMax-M2.7-highspeed'),
  enabled: getEnvBool('MINIMAX_ENABLED', false),
},
```

## Build and install
```bash
cd /path/to/mercury-agent
npm run build
npm uninstall -g @cosmicstack/mercury-agent
npm install -g .
```

## Configure
Edit `~/.mercury/mercury.yaml`:
```yaml
providers:
  default: minimax
  minimax:
    name: minimax
    apiKey: YOUR_MINIMAX_API_KEY
    baseUrl: https://api.minimax.io/anthropic/v1
    model: MiniMax-M2.7-highspeed
    enabled: true
  openai:
    enabled: false
```

## Restart
```bash
mercury stop
mercury up
```

## Key pitfalls
- **Must use `/v1` in baseUrl** — MiniMax endpoint is `https://api.minimax.io/anthropic/v1/messages`, NOT just `/anthropic/messages`. Without `/v1` you get 404.
- **MiniMax returns thinking blocks** — The model returns `thinking` content blocks that must be filtered. The `generateText` handler extracts only `text` blocks from `result.raw.content`.
- **Anthropic SDK required** — OpenAI SDK calls `/chat/completions` which 404s on MiniMax. Must use `@ai-sdk/anthropic` with `createAnthropic()`.
