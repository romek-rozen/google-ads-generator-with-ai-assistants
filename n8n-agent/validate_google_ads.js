/**
 * n8n Code Tool: validate_google_ads
 *
 * Description:
 * Validates Google Ads against character limits and count requirements.
 * Input: ads object with headlines, descriptions, and paths arrays.
 * Returns validation results with specific errors to fix.
 */

// When using schema, query is already an object
const ads = query.ads || query;

// Limits
const limits = { headline: 30, description: 90, path: 15 };
const countReq = {
  headlines: { min: 3, max: 15 },
  descriptions: { min: 2, max: 4 },
  paths: { min: 2, max: 2 }
};

const errors = [];
const issues = [];

// Validate headlines
const headlines = ads.headlines || [];
if (headlines.length < countReq.headlines.min) {
  errors.push(`Headlines: minimum ${countReq.headlines.min} required, got ${headlines.length}`);
} else if (headlines.length > countReq.headlines.max) {
  errors.push(`Headlines: maximum ${countReq.headlines.max} allowed, got ${headlines.length}`);
}

headlines.forEach((h, i) => {
  const len = h.length;
  if (len > limits.headline) {
    issues.push(`Headline ${i + 1}: "${h}" - ${len}/${limits.headline} chars (TOO LONG by ${len - limits.headline})`);
  }
});

// Validate descriptions
const descriptions = ads.descriptions || [];
if (descriptions.length < countReq.descriptions.min) {
  errors.push(`Descriptions: minimum ${countReq.descriptions.min} required, got ${descriptions.length}`);
} else if (descriptions.length > countReq.descriptions.max) {
  errors.push(`Descriptions: maximum ${countReq.descriptions.max} allowed, got ${descriptions.length}`);
}

descriptions.forEach((d, i) => {
  const len = d.length;
  if (len > limits.description) {
    issues.push(`Description ${i + 1}: "${d.substring(0, 30)}..." - ${len}/${limits.description} chars (TOO LONG by ${len - limits.description})`);
  }
});

// Validate paths
const paths = ads.paths || [];
if (paths.length !== countReq.paths.min) {
  errors.push(`Paths: exactly ${countReq.paths.min} required, got ${paths.length}`);
}

paths.forEach((p, i) => {
  const len = p.length;
  if (len > limits.path) {
    issues.push(`Path ${i + 1}: "${p}" - ${len}/${limits.path} chars (TOO LONG by ${len - limits.path})`);
  }
});

// Build result
const allValid = errors.length === 0 && issues.length === 0;

let result = allValid
  ? "VALID: All ads pass validation!\n\n"
  : "INVALID: Fix the following issues:\n\n";

if (errors.length > 0) {
  result += "COUNT ERRORS:\n" + errors.map(e => "- " + e).join("\n") + "\n\n";
}

if (issues.length > 0) {
  result += "LENGTH ISSUES:\n" + issues.map(i => "- " + i).join("\n") + "\n\n";
}

result += `SUMMARY:\n- Headlines: ${headlines.length} (valid: ${headlines.filter(h => h.length <= limits.headline).length})\n`;
result += `- Descriptions: ${descriptions.length} (valid: ${descriptions.filter(d => d.length <= limits.description).length})\n`;
result += `- Paths: ${paths.length} (valid: ${paths.filter(p => p.length <= limits.path).length})`;

return result;
