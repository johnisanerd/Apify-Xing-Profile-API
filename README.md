# 🇩🇪 Xing API: turn Xing profile URLs into structured JSON

> Bring the profile URLs, get back name, job title, city, skills, languages, and the full role history as clean JSON. Python and MCP examples in this repo.

**Actor page:** [apify.com/johnvc/xing-profile-api](https://apify.com/johnvc/xing-profile-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/xing-profile-api/input-schema](https://apify.com/johnvc/xing-profile-api/input-schema?fpr=9n7kx3)

This repo is a working example of the Xing API on Apify. You pass a list of member profile URLs (a bare handle such as `Jane_Doe` works too) and each profile comes back as one JSON row holding whatever that member published: identity, current role, city and country, listed skills in German and English, spoken languages, employment history, education, groups, and interests. Xing is the professional network of the German-speaking world, so it holds people who are not on the global networks, which makes it a distinct source for DACH recruiting and market research rather than a substitute. There is no discovery endpoint, so this API reads profiles you already hold URLs for; it does not search for people by title, company, or city.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The Xing API takes exactly one input, `profileUrls`, an array of up to 1000 member profile URLs or bare handles per run. Every collected entry returns a row whose `result_type` is `profile`, carrying the fields that member published, drawn from `fullName`, `jobTitle`, `city`, `countryCode`, `membership`, `skills`, `languages`, `experience`, `education`, `groups`, and `interests`, plus a one-line `summary` an agent can read without post-processing. An input that cannot be collected returns a row with `result_type` of `error` and a plain-language `error_message`, so nothing disappears quietly. A concrete use: you have shortlisted twenty candidates in Munich from a job board and hold their profile links, so you run them through the API in one batch and get each person's role history, tenure, and listed skills in a single table you can sort. The same call powers a Kandidatensuche follow-up step, enriching a German-market shortlist that you built somewhere else. Skills come back exactly as the member typed them, which in practice means German and English mixed in the same list. No email addresses or phone numbers are returned, because profiles do not publish them.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-Xing-Profile-API.git
   cd Apify-Xing-Profile-API
   ```

2. **Install dependencies with UV**
   ```bash
   # Install UV if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python xing-profile-api-example.py

   # Role and education history for a small batch:
   uv run python xing-profile-api-example.py --example career
   ```

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python xing-profile-api-example.py
```

The default run asks for a single profile on purpose. Billing is per profile returned, so one URL keeps the first run to a fraction of a cent. Raise the list size once you know your budget.

## Why Use This Xing API?

**It covers people the global networks miss.** The German-speaking market keeps a large share of its professional presence here, and a DACH shortlist assembled anywhere else will have gaps that these profiles fill.

**One input, no configuration.** There is a single parameter. You send URLs or handles, you get rows. Nothing to tune, no pagination to manage, no session to keep alive.

**Career history arrives structured.** `experience` is an array of employers with the job title and dates the member published, and `education` is an array of institutions and qualifications. You do not parse a resume blob; you read fields.

**Batches are honest about failures.** A URL that returns nothing produces an error row rather than a silent gap, and it is not billed, so a 200-URL batch reconciles cleanly against what you paid for.

**Agents can read it directly.** Each row carries a `summary` string that states who the person is in one sentence, which saves an LLM round trip when the API is wired in over MCP.

## Features

### Core Capabilities
- Collect up to 1000 Xing profiles per run from URLs or bare handles
- Identity fields: `fullName`, `givenName`, `familyName`, `honorificPrefix`, `profileId`, `imageUrl`
- Current position: `jobTitle`, `city`, `countryCode`, `membership`
- Full employment history in `experience` and schooling in `education`
- `skills` and `languages` as listed by the member, German and English as entered
- Community context: `groups` and `interests`, plus `similarProfiles`
- Two ready-made dataset views on the Store, Profile overview and Career history, plus JSON, CSV, and Excel export

### Data Quality
- Every row is tagged `result_type` of `profile` or `error`, so batches reconcile
- Fields a member did not publish are omitted rather than returned empty, so a sparse profile reads as sparse instead of broken
- `fetched_at` carries the UTC timestamp of collection on every row
- Skills and languages are returned verbatim, not translated or normalised
- No contact details are returned: profiles carry role and history, not email addresses or phone numbers

## Xing profiles in, structured rows out

The three sections below are the field reference: what you send, what the parameters mean, and what comes back. The output sample is a real row from a run of this repo's quick-start, with the `similarProfiles` list trimmed for length.

### Usage Examples

#### Basic Example
```json
{
  "profileUrls": [
    "https://www.xing.com/profile/Chuck_Coulson"
  ]
}
```

#### Advanced Example
```json
{
  "profileUrls": [
    "https://www.xing.com/profile/Chuck_Coulson",
    "Andreas_Lappano",
    "https://www.xing.com/profile/Jane_Doe"
  ]
}
```

Full URLs and bare handles can be mixed in one call. Duplicates are removed before collection.

### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `profileUrls` | `list[str]` | YES | - | Member profile URLs, for example `https://www.xing.com/profile/Jane_Doe`. A bare handle such as `Jane_Doe` also works. Up to 1000 per run. |

That is the whole input. There is no query, city, or skill filter, because the source offers no discovery endpoint.

### Output Format

```json
{
  "result_type": "profile",
  "profileId": "19268017.0f55c9",
  "fullName": "Chuck Coulson",
  "givenName": "Chuck",
  "familyName": "Coulson",
  "profileUrl": "https://www.xing.com/profile/Chuck_Coulson",
  "jobTitle": "VP, Business Development & Alliances",
  "city": "Cupertino",
  "countryCode": "US",
  "membership": "BASIC",
  "imageUrl": "https://profile-images.xing.com/images/1e7192e2ce7fa1a7252ac390a9d379fb-1/chuck-coulson.1024x1024.jpg",
  "skills": [
    "Business Development",
    "Alliances",
    "Strategic Partners",
    "SaaS",
    "CRM",
    "International Business"
  ],
  "languages": ["Englisch"],
  "experience": [
    { "company": "Helpshift" },
    { "company": "Google" },
    { "company": "SugarCRM" },
    { "company": "Parature" },
    { "company": "SAP America" },
    { "company": "salesforce.com" },
    { "company": "Oracle" }
  ],
  "education": [
    { "qualification": "Information Systems" }
  ],
  "similarProfiles": [
    "https://www.xing.com/profile/Eugen_Racovita",
    "https://www.xing.com/profile/Gunnar_Habitz"
  ],
  "summary": "Chuck Coulson, VP, Business Development & Alliances, based in Cupertino. 7 role(s) on record, 6 listed skill(s).",
  "fetched_at": "2026-08-07T17:44:47.742034+00:00"
}
```

`experience` entries carry `company` plus `title`, `startDate`, and `endDate` when the member published them. `education` entries carry `institution`, `qualification`, and dates on the same terms. An input that returned nothing looks like this instead:

```json
{
  "result_type": "error",
  "sourceUrl": "https://www.xing.com/profile/Not_A_Real_Handle",
  "error_message": "No profile was returned.",
  "error_type": "CollectionError",
  "fetched_at": "2026-08-07T17:44:47.742034+00:00"
}
```

## Kandidatensuche: Profile anreichern statt suchen

Dieser Actor durchsucht Xing nicht. Er liest Profile aus, deren URL oder Handle Sie bereits haben. Der uebliche Ablauf fuer eine Kandidatensuche im DACH-Raum: Sie sammeln Kandidaten in einer Jobboerse, einem ATS oder einer Empfehlungsliste, uebergeben die Profil-URLs hier in einem Lauf und erhalten pro Person aktuellen Job, Werdegang, Ausbildung, Kenntnisse und Sprachen als strukturierte Zeile. Danach filtern Sie das Ergebnis nach `skills`, `city` oder `jobTitle`, ganz wie es Ihr Prozess braucht. Kontaktdaten sind nicht enthalten.

## People also search for

### Is this a Xing scraper or an API?

This repo teaches the **Xing API** on Apify. People search for scraping tools when what they want is structured profile data, and this Actor covers that need: send URLs, get JSON you can call from Python or from an MCP client.

### Was ist ein Xing Profil?

Ein Xing Profil ist die berufliche Profilseite eines Mitglieds im deutschsprachigen Karrierenetzwerk: aktueller Job, Werdegang, Ausbildung, Kenntnisse und Sprachen. Diese API liefert genau diese Angaben als strukturiertes JSON.

### Wer kann mein Xing Profil sehen?

Das entscheidet das Mitglied selbst ueber seine Sichtbarkeitseinstellungen. Diese API liest ausschliesslich, was ein Profil oeffentlich zeigt, und gibt Felder ohne Wert gar nicht erst aus.

### Wie finde ich Kandidaten auf Xing?

Nicht mit dieser API. Sie hat keinen Suchmodus, weil die Quelle keinen anbietet. Starten Sie die Kandidatensuche an anderer Stelle und uebergeben Sie die gefundenen Profil-URLs hier zur Anreicherung.

### How do I export Xing profile data?

Run the Actor with your profile URLs, then export the dataset as JSON, CSV, or Excel from the Output tab, or read it from Python as this repo's example does. Every profile is one row, and the Career history view puts roles and education side by side.

### How do I use the Xing API from Python?

Clone this repo, set `APIFY_API_TOKEN`, and run `uv run python xing-profile-api-example.py`. See Quick Start above. The example uses `apify-client` 3.x, where `.call()` returns a run object and the dataset is read from `run.default_dataset_id`.

### Can I use the Xing API with MCP or Claude?

Yes. Use the install sections below to add the Actor as an MCP tool in [Claude Code](https://claude.ai/referral/uIlpa7nPLg) (free trial), [Claude Cowork](https://claude.ai/referral/uIlpa7nPLg) (free trial), Claude.ai, Cursor, or ChatGPT.

### Can I search for candidates by skill or city?

Not with this API, because the source has no discovery endpoint. Once profiles are collected you can of course filter the rows by `skills`, `city`, or `jobTitle`.

### Does it work for profiles outside Germany?

Yes. The network is strongest in Germany, Austria, and Switzerland, but members list locations worldwide and the API returns whatever the profile holds.

**Schedule tip:** Save your input as an Apify Task and [schedule it on the Actor page](https://apify.com/johnvc/xing-profile-api?fpr=9n7kx3) to run weekly or monthly, so a tracked list of profiles refreshes itself and you notice job changes without running anything by hand.

---

<!-- MCP install sections. The Actor's MCP server URL is:
     https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api -->

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Xing API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Xing API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Xing API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/xing-profile-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api`, using OAuth when prompted.
5. Ask Claude to run the Xing API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Xing API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/xing-profile-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## Related APIs

- [LinkedIn Profile API](https://apify.com/johnvc/linkedin-profile-api?fpr=9n7kx3) for the same shape of data on the global network
- [LinkedIn Jobs API](https://apify.com/johnvc/linkedin-jobs-api?fpr=9n7kx3) for open roles
- [Workday Careers API](https://apify.com/johnvc/workday-careers-api?fpr=9n7kx3) for employer-side job listings
- [Glassdoor Reviews API](https://apify.com/johnvc/glassdoor-reviews-api?fpr=9n7kx3) for employer reputation

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/xing-profile-api/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Xing API to power your DACH talent and market research workflows with reliable, structured results.*

Last Updated: 2026.08.08
