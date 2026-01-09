/**
 * n8n Code Tool: check_text_length
 *
 * Description:
 * Checks text length against a specified limit. Use before adding text to ads.
 * Input: text (required), limit (optional, default 30).
 */

// When using schema, query is already an object (not string)
const text = query.text || "";
const limit = query.limit || 30;

const length = text.length;
const valid = length <= limit;
const remaining = limit - length;

const status = valid
  ? `OK (${remaining} chars remaining)`
  : `TOO LONG by ${Math.abs(remaining)} chars`;

return `Text: "${text}"\nLength: ${length}/${limit}\nValid: ${valid}\nStatus: ${status}`;
