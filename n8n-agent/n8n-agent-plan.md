# Plan: Google Ads Writer Agent in n8n

## Goal
Create an n8n workflow that acts as an agent for generating Google Ads (RSA) based on website content.

## Architecture

```
┌─────────────────┐
│   Chat Trigger  │  ← User provides URL and optional guidelines
└────────┬────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│                    AI Agent (GPT-4o)                │
│                                                     │
│  System prompt: Google Ads RSA Expert               │
│  - Knows character limits (headline: 30, desc: 90)  │
│  - Generates ads in JSON format                     │
│  - Validates before returning results               │
└────────┬────────────────────────────────────────────┘
         │
         ├──→ [Tool 1: Web Scraper]
         │    Calls existing workflow: Ln7kOpsx2ZzYh0Te
         │    Input: Website URL
         │    Output: markdown + meta tags
         │
         ├──→ [Tool 2: Validate Google Ads]
         │    Code node with validation logic
         │    Checks: text length, element count
         │    Returns: errors or OK
         │
         └──→ [Tool 3: Check Text Length]
              Simple helper to check text length
              Returns: text + character count
```

## Components to Create

### 1. Main Workflow: "Google Ads Writer Agent"

**Nodes:**

1. **Chat Trigger** (`@n8n/n8n-nodes-langchain.chatTrigger`)
   - Public chat interface
   - Title: "Google Ads Writer"
   - Description: "Provide a website URL and I'll generate Google Ads"

2. **AI Agent** (`@n8n/n8n-nodes-langchain.agent`)
   - Model: Gemini 2.5 Flash (OpenRouter)
   - System message with agent instructions (below)
   - Max iterations: 10
   - Connected tools (3 total)

3. **OpenRouter Chat Model** (`@n8n/n8n-nodes-langchain.lmChatOpenRouter`)
   - Model: google/gemini-2.5-flash
   - Temperature: 0.7

4. **Window Buffer Memory** (`@n8n/n8n-nodes-langchain.memoryBufferWindow`)
   - Preserves conversation context

### 2. Agent Tools

#### Tool 1: Web Scraper (Call n8n Workflow)
- Node: `@n8n/n8n-nodes-langchain.toolWorkflow`
- Calls: `Ln7kOpsx2ZzYh0Te` (_tool web scraper)
- Name: `scrape_website`
- Description: "Fetches website content. Provide URL."
- Input schema: `{ "query": "Website URL" }`

#### Tool 2: Validate Google Ads (Code Tool)
- Node: `@n8n/n8n-nodes-langchain.toolCode`
- Name: `validate_google_ads`
- Description: "Validates Google Ads. Checks character limits and element counts."

#### Tool 3: Check Text Length (Code Tool)
- Node: `@n8n/n8n-nodes-langchain.toolCode`
- Name: `check_text_length`
- Description: "Checks text length. Use before adding to ad."
- Code:

### 3. System Prompt for AI Agent

See `system-prompt-interactive.md` for the full prompt with copywriting frameworks.

## Implementation Steps

### Step 1: Create Workflow
```
Create workflow with:
- name: "Google Ads Writer Agent"
- nodes: [Chat Trigger, AI Agent, OpenRouter Model, Memory, 3x Tools]
- connections: appropriate links
```

### Step 2: Configure Credentials
- Ensure OpenRouter credentials are configured in n8n

### Step 3: Testing
1. Activate workflow
2. Open chat interface
3. Enter website URL (e.g., "https://example.com")
4. Verify that agent:
   - Fetches the page
   - Generates ads
   - Validates
   - Fixes if needed

## Verification

### Test 1: Basic Flow
- Input: "Generate ads for https://example.com"
- Expected result: Agent fetches page, generates ads, validates, returns JSON

### Test 2: Error Validation
- Manually call validate_google_ads with texts that are too long
- Verify it returns correct errors

### Test 3: Iteration
- Provide URL and ask for "more creative headlines"
- Verify agent maintains context (memory)

## Files to Modify
- None (creating new workflow in n8n)

## Dependencies
- Existing workflow: (_tool web scraper)
- OpenRouter API credentials in n8n
- Redis (used by scraper - already configured)
