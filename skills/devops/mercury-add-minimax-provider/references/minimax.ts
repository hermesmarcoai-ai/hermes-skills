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
