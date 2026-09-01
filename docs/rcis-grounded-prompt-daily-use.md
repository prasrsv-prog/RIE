# RCIS Grounded Prompt Daily Use

This guide describes the published local single-operator flow.

## Launch

From the repository root, run `run-rcis-grounded-prompt-ui.cmd`.
The launcher does not install dependencies.
The launcher does not start a network service.

## Start a grounded prompt request

1. Click `Browse...` and select the intended Intake Root.
2. Click `Load Foundation` explicitly.
3. Select the Product ID explicitly.
4. Select the Variant ID explicitly.
5. Enter Background explicitly.
6. Enter Camera Angle explicitly.
7. Enter Requested Output explicitly.
8. Click `Submit Grounded Prompt` explicitly.
9. Review the four visible grounding statuses and the compiled grounded prompt.

The UI has no hidden defaults.
The UI has no automatic product or variant selection.
The UI performs no automatic prompt rewriting.

## Copy the compiled prompt

Select the prompt text and use `Ctrl+C`.
The prompt remains read-only and no custom clipboard action is required.

## Repeat or correct a request

Changing any result-defining input clears the rendered prompt and the four rendered success statuses.
After changing an input, explicitly submit again when the request is ready.
Changing Product ID continues to clear Variant ID so the operator must select a variant explicitly.

The application does not persist request history.
The application does not provide saved presets.
The application does not remember hidden operator defaults.

A failed submit remains fail-closed and does not retain prior rendered success output.

## Exit

When daily work is finished, close the RCIS window normally.

The local UI does not invoke an external AI model.
It does not invoke an image generator or video generator.
Local AI Generator Integration is not required for this workflow.


## Save a prompt to a text file

After a successful current result shows **Prompt ready**, choose **Save prompt...** to save the generated prompt as a normal text file. RCIS opens the native **Save As** dialog with `RCIS-grounded-prompt.txt` as the suggested filename. You choose the destination; RCIS does not force Downloads, Documents, the repository, the governed intake, or the installation directory.

The saved `.txt` file contains exactly the generated prompt text as UTF-8 bytes. RCIS adds no metadata, product or variant IDs, status fields, labels, header, footer, BOM, newline translation, or extra final newline.

In **Recent**, select one stored prompt and choose **Save selected prompt...** to save that stored prompt text directly. You do not need to open or duplicate the prompt first, and saving does not change the Recent record.

Canceling **Save As** changes nothing and is not an error. If the destination cannot be written, RCIS keeps the prompt and workspace available, shows a friendly recoverable error with technical detail in **View Details**, and does not silently delete or repair a partially created file. Choose **Save prompt...** again after resolving the destination or permission problem.

**Copy Prompt** and **Copy Prompt** in Recent remain available for clipboard use and are unchanged by file saving.
