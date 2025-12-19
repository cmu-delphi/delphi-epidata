---
title: Documentation Features Tutorial
nav_exclude: true
search_exclude: true
---

# Documentation Features Tutorial
{: .no_toc}


## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Callouts

You can use blockquotes with specific classes to create callouts for notes, warnings, and other important information.

### Syntax

Use the following syntax:

```markdown
> **Label:** Your text here.
{: .class-name }
```

### Available Classes

#### Note
```markdown
> **Note:** This is a note.
{: .note }
```
> **Note:** This is a note.
{: .note }

#### Important
```markdown
> **Important:** This is important information.
{: .important }
```
> **Important:** This is important information.
{: .important }

#### Warning
```markdown
> **Warning:** This is a warning.
{: .warning }
```
> **Warning:** This is a warning.
{: .warning }

#### Tip
```markdown
> **Tip:** This is a helpful tip.
{: .tip }
```
> **Tip:** This is a helpful tip.
{: .tip }

#### Caution
```markdown
> **Caution:** Proceed with caution.
{: .caution }
```
> **Caution:** Proceed with caution.
{: .caution }

## Code Tabs

### Structure

The structure consists of a container `div` with class `code-tabs`, a header `div` with class `tab-header` containing buttons, and multiple content `div`s with class `tab-content`.

**Key Requirements:**
1.  **Container:** `<div class="code-tabs">`
2.  **Header:** `<div class="tab-header">` containing `<button>` elements.
3.  **Buttons:** Each button must have a `data-tab` attribute (e.g., `data-tab="python"`). One button should have the class `active`.
4.  **Content:** Each content div must have the class `tab-content` and a matching `data-tab` attribute. The default active tab must also have the class `active`.
5.  **Markdown Parsing:** Add `markdown="1"` to the content divs to ensure the code blocks inside are parsed correctly.

### Example

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
    <button data-tab="curl">cURL</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

```python
import pandas as pd
```

  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```r
library(covidcast)
```
  </div>

  <div class="tab-content" data-tab="curl" markdown="1">

```bash
curl ...
```
  </div>
</div>

### Source Code for Example

```html
    <div class="code-tabs">
      <div class="tab-header">
        <button class="active" data-tab="python">Python</button>
        <button data-tab="r">R</button>
        <button data-tab="curl">cURL</button>
      </div>

      <div class="tab-content active" data-tab="python" markdown="1">

    ```python
    import pandas as pd
    ```

      </div>

      <div class="tab-content" data-tab="r" markdown="1">

    ```r
    library(covidcast)
    ```

      </div>

      <div class="tab-content" data-tab="curl" markdown="1">

    ```bash
    curl ...
    ```

      </div>
    </div>
```
