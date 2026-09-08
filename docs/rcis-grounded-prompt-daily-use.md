# RCIS Grounded Prompt Daily Use

This guide describes the current local single-operator desktop flow.

## Launch

For a packaged Windows installation, use the installed RCIS shortcut.

From a repository checkout, run `run-rcis-grounded-prompt-ui.cmd` from the repository root. The repository launcher does not install dependencies and does not start a network service.

## Start a grounded prompt request

1. Open **New Prompt**.
2. Use the remembered Data Source when it is already correct. To change it, open **Data Source**, choose **Browse...**, select the intended Intake Root, and choose **Load Foundation** explicitly.
3. Select the human-friendly Product and Variant labels.
4. Enter Background.
5. Enter Camera Angle.
6. Enter Requested Output.
7. Choose **Generate Prompt**.
8. Review the **Prompt ready** result. Use **View Details** when technical grounding details are needed.

RCIS does not automatically rewrite Requested Output and does not invoke an external AI model as part of this local grounding workflow. Local AI Generator Integration is not required for this workflow.

## Reuse daily work

RCIS keeps a local operator workspace for repeat work:

- **Recent** stores recently generated prompts. Select a row to see its read-only Product / Variant, Background, Camera Angle, and Requested Output context, then open the stored result, duplicate its request, copy the exact stored prompt, save it to a text file, or mark it as a favorite.
- **Presets** stores named request configurations. Select a preset to see its read-only Preset Name, Product / Variant, Background, Camera Angle, and Requested Output context, then load or delete it later.
- **Products** lists available product / variant combinations with human-friendly labels. A product variant can be favorited or set as the explicit default for a new request.
- **Settings** shows the current default and keeps Data Source recovery available.

An explicit default product / variant is visible operator workspace state; it is not a hidden Background, Camera Angle, or Requested Output value. The operator can change the selected Product or Variant before generating.

The workspace is local operator convenience state. It does not change governed evidence, product identity, or grounding semantics.

## Search and filter the workspace

**Recent**, **Presets**, and **Products** each have a **Search / Filter** field.

Filtering is case-insensitive and deterministic:

- Recent matches the displayed Product / Variant label plus Background, Camera Angle, and Requested Output. Stored prompt text itself is not part of the Recent search surface.
- Presets matches the preset name plus Product / Variant, Background, Camera Angle, and Requested Output.
- Products matches the displayed Product / Variant label.
- Favorite markers do not participate in matching.

Clearing a filter restores the complete list in its original order. A filter with no matches shows an empty list. Filter text is temporary UI state and is not written to the persisted local workspace.

The selected Recent context preview is also temporary UI state. It clears when no valid Recent row is selected, including after a filter refresh removes the selected row, and it is not written to the persisted local workspace.

The selected Preset context preview is temporary UI state as well. It clears when no valid Preset row is selected, including after a filter refresh removes the selected row, and it is not written to the persisted local workspace.

Actions on a filtered row continue to operate on the exact underlying Recent item, preset, or product / variant pair.

## Copy or save a prompt

Use **Copy Prompt** for the current generated prompt or a selected Recent prompt.

After a successful current result shows **Prompt ready**, choose **Save prompt...** to save the generated prompt as a normal text file. RCIS opens the native **Save As** dialog with `RCIS-grounded-prompt.txt` as the suggested filename. You choose the destination.

The saved `.txt` file contains exactly the generated prompt text as UTF-8 bytes. RCIS adds no metadata, product or variant IDs, status fields, labels, header, footer, BOM, newline translation, or extra final newline.

In **Recent**, choose **Save selected prompt...** to save the exact stored prompt directly without opening or duplicating it first.

Canceling **Save As** changes nothing and is not an error. If the destination cannot be written, RCIS keeps the prompt and workspace available and exposes recoverable technical detail through **View Details**.

## Repeat, correct, or start another request

Changing a result-defining input clears the rendered result and its rendered grounding status so stale success is not presented as current. Generate again after the corrected request is ready.

**New Request** clears the current request while preserving local Recent, Presets, favorites, and the explicit default product / variant.

## Exit

When daily work is finished, close the RCIS window normally.

Phase O general-user usability proof remains a separate unresolved governance activity and is not implied by these daily-use capabilities.
