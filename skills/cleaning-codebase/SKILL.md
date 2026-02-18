---
name: cleaning-codebase
description: Safely identifies and removes unused code, files, and dependencies without breaking running functionality. Use when the user asks to "clean up", "remove unused code", or "optimize" the codebase.
---

# Cleaning Codebase Skill

## When to use this skill
- When the user asks to remove "unused code", "dead code", or "extra files".
- When you need to declutter the project before a major refactor or deployment.

## Core Principles
1.  **Safety First**: Never delete code without verifying it is truly unused.
2.  **Incremental**: Clean one component or module at a time.
3.  **Verification**: Always run the build/dev server after deletion to ensure no breakages.
4.  **Preservation**: If unsure, comment out code instead of deleting it, or ensure version control is active.

## Workflow

### 1. Analysis Phase
Before deleting anything, identify candidates for removal.

-   **Unused Exports**: Look for exported components/functions that are never imported.
    -   *Technique*: Search for the string `export const ComponentName` and then search for `ComponentName` usage across the codebase.
-   **Unused Imports**: Look for greyed-out imports in your IDE view, or imports that are never referenced in the file.
-   **Ghost Files**: Files that are not imported by any other file in the project (excluding pages/routes).

### 2. Execution (Safe Removal)

#### A. Removing Unused Components/Files
1.  **List Candidates**: Create a list of files you suspect are unused.
2.  **Verify Usage**: Run `grep_search` for the filename (without extension) to see if it's imported anywhere.
    > `grep_search(SearchPath="./src", Query="MyComponent")`
3.  **Delete**: If 0 results (other than the definition itself), delete the file.
    > `run_command("rm src/components/MyComponent.tsx")`

#### B. Cleaning Inside Files
1.  **Unused Variables/Imports**:
    -   Read the file content.
    -   Identify variables declared but not used.
    -   Remove them precisely using `replace_file_content`.

### 3. Verification Phase
After **every** batch of deletions:
1.  **Build Check**: Run the build process to catch missing dependencies.
    > `npm run build` (or equivalent)
2.  **Runtime Check**: If the build passes, briefly check the dev server output for runtime errors.
3.  **Rollback**: If the build fails, immediately restore the deleted file/code.

## Common Pitfalls
-   **Dynamic Imports**: Be careful with `next/dynamic` or `React.lazy` imports which might not show up in static analysis.
-   **Pages/Routes**: In frameworks like Next.js, files in `pages/` or `app/` are entry points and won't be imported elsewhere. **Do not delete them** unless explicitly asked.
-   **Config Files**: Files like `tailwind.config.js`, `postcss.config.js`, etc., are often not imported but are critical.

## Checklist
- [ ] Identify unused files/code.
- [ ] Verify no dynamic usage.
- [ ] Delete/Remove.
- [ ] Run Build/Test.
- [ ] Commit changes.
