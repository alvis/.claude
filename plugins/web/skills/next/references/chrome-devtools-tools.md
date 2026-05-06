# Chrome DevTools MCP -- Tool Reference

## Input
- `click(x, y)` -- click at coordinates
- `type(text)` -- type text into focused element
- `press_key(key)` -- press a keyboard key
- `hover(x, y)` -- hover at coordinates
- `drag(startX, startY, endX, endY)` -- drag between coordinates
- `select_option(selector, value)` -- select dropdown option
- `check_checkbox(selector)` -- toggle checkbox
- `upload_file(selector, path)` -- upload file to input
- `dismiss_dialog` -- dismiss alert/confirm/prompt dialog

## Navigation
- `navigate(url)` -- navigate to URL
- `go_back` -- browser back
- `go_forward` -- browser forward
- `reload` -- reload page
- `wait_for_navigation` -- wait for navigation to complete
- `wait_for_selector(selector)` -- wait for element to appear

## Snapshot & DOM
- `take_snapshot` -- capture accessibility tree snapshot of the page
- `evaluate_script(expression)` -- execute JS in page context, return result
- `take_screenshot` -- capture page screenshot as PNG

## Emulation
- `emulate(device)` -- emulate a device (e.g., "iPhone 14", "iPad Pro")
- `resize_page(width, height)` -- set viewport size

## Performance
- `performance_start_trace` -- start CPU/timeline trace
- `performance_stop_trace` -- stop trace and return results
- `take_memory_snapshot` -- capture heap snapshot
- `lighthouse_audit` -- run Lighthouse audit (performance, a11y, SEO, best practices)

## Network & Console
- `list_network_requests` -- list captured network requests with status, timing, size
- `list_console_messages` -- list console messages (log, warn, error, info)

## Debugging
- `set_breakpoint(url, line)` -- set JS breakpoint
- `remove_breakpoint(id)` -- remove breakpoint
- `pause` -- pause JS execution
- `resume` -- resume JS execution
- `step_over` -- step over next statement
- `get_call_stack` -- get current call stack frames
