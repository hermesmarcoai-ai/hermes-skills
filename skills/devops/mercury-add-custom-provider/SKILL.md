---
name: mercury-add-custom-provider
description: Add a custom LLM provider to Mercury Agent (e.g. MiniMax). Covers the 4-file pattern, the missing-import bug, and verification.
triggers:
  - "add provider to mercury"
  - "mercury custom model"
  - "mercury minimax provider"
---

# Adding a Custom Provider to Mercury Agent

## When to Use
When you need to add a new LLM provider to Mercury Agent that isn't natively supported (e.g., MiniMax, custom endpoints).

## Files to Modify
1. `src/providers/<name>.ts` — new provider class
2. `src/providers/index.ts` — export the new provider
3. `src/providers/registry.ts` — import + case in constructor + add to entries array
4. `src/utils/config.ts` — add to ProviderName type union + MercuryConfig interface + getDefaultConfig

## Step-by-Step

### 1. Create the provider file
Copy `src/providers/anthropic.ts` as template. The key pattern:
```typescript
export class <Name>Provider extends BaseProvider {
  readonly name = '<name>';
  readonly model: string;
  private client: ReturnType<typeof createAnthropic>;
  private modelInstance: ...

  constructor(config: ProviderConfig) {
    super(config);
    this.model = config.model;
    this.client = createAnthropic({
      apiKey: config.apiKey,
      baseURL: config.baseUrl || '<default-base-url>',
    });
    this.modelInstance = this.client(config.model);
  }
  // ... implement generateText, streamText, isAvailable, getModelInstance
}
```

### 2. Export from index.ts
```typescript
export { <Name>Provider } from './<name>.js';
```

### 3. Update registry.ts — THREE changes needed
```typescript
// Change 1: IMPORT
import { <Name>Provider } from './<name>.js';

// Change 2: Add to entries array in constructor
const entries: ProviderConfig[] = [
  // ... existing entries ...
  config.providers.<name>,
];

// Change 3: Add case in the if/else chain
if (pc.name === 'anthropic') {
  provider = new AnthropicProvider(pc);
} else if (pc.name === '<name>') {
  provider = new <Name>Provider(pc);
} else if (pc.name === 'ollamaCloud' || pc.name === 'ollamaLocal') {
  // ...
}
```

### 4. Update config.ts — THREE changes needed
```typescript
// Change 1: Add to ProviderName type union
export type ProviderName =
  | 'openai'
  | 'anthropic'
  // ... existing ...
  | '<name>';

// Change 2: Add to MercuryConfig interface
providers: {
  // ... existing ...
  <name>: ProviderConfig;
};

// Change 3: Add to getDefaultConfig()
<name>: {
  name: '<name>',
  apiKey: getEnv('<NAME>_API_KEY', ''),
  baseUrl: getEnv('<NAME>_BASE_URL', '<default-url>'),
  model: getEnv('<NAME>_MODEL', '<default-model>'),
  enabled: getEnvBool('<NAME>_ENABLED', false),
},
```

### 5. Build and reinstall
```bash
npm run build
npm install -g .
```

## Critical Pitfall
**The import in registry.ts is easy to forget.** If you get `ReferenceError: <Name>Provider is not defined`, you missed the import statement in `src/providers/registry.ts`.

## Verification
```bash
mercury start --verbose 2>&1 | grep -i "provider\|model"
# Should show: Provider registered, model: <model-name>
```
