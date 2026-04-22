---
name: openrouter-model-check
description: A skill to check pricing and availability of models on OpenRouter.
---

## Overview
This skill outlines the steps to verify the pricing status of a specific model on OpenRouter, including handling issues with page loading and non-responsiveness.

## Steps
1. **Navigate to the Model Page**: Use the `browser_navigate` tool to go to the model's URL.
   - Example: `https://openrouter.ai/qwen/qwen3.6-plus:free`

2. **Check for Navigation Success**: If navigation fails due to timeouts, retry or handle exceptions as necessary.

3. **Check for Connectivity Issues**: If navigation fails due to `net::ERR_TUNNEL_CONNECTION_FAILED`, log the error and attempt to navigate to alternative URLs or inform about the inability to access the page.: Once the page is loaded, use `browser_snapshot` to capture relevant content.

4. **Look for Pricing Information**: Analyze the snapshot for pricing details:
   - Look for `$0` or `Free` to determine if the model is still free.
   - Identify any dollar amounts indicating the model is now paid.
   - Check for "not found" messages indicating the model may be removed.

5. **Output Results Based on Findings**:
   - If the model is free, output nothing.
   - If it is paid, report the new pricing information.
   - If removed/not found, report as such.

## Notes
- Adjust navigation attempts in case of timeouts to ensure access to the page.
- Use proper exception handling to manage potential issues encountered during the check.
- The skill accommodates checking various models by adjusting the URL in step 1.
