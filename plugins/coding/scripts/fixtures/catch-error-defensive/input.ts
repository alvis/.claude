export function handleA(): string {
  try {
    return doWork();
  } catch (error) {
    return error instanceof Error ? error.message : String(error);
  }
}

export function handleB(): string {
  try {
    return doWork();
  } catch (err) {
    const detail = String(err);
    return detail;
  }
}

export function handleClean(): string {
  try {
    return doWork();
  } catch (e) {
    if (e instanceof Error) {
      return e.message;
    }
    return 'unknown';
  }
}

function doWork(): string {
  return 'ok';
}
