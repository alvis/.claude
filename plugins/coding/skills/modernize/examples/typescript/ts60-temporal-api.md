---
since: "TS 6.0"
min-es-target: "esnext"
module: "any"
---

## Detection

`new Date()`
`Date.now()`
`moment()`
`dayjs(`
`date-fns`
manual date arithmetic using `getTime() + 86400000`

## Before

```typescript
import moment from "moment";

// Creating dates
const now = new Date();
const timestamp = Date.now();

// Date arithmetic — error-prone magic numbers
const tomorrow = new Date(now.getTime() + 86400000);
const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

// Formatting with moment
const formatted = moment().format("YYYY-MM-DD");
const inTwoDays = moment().add(2, "days").toDate();

// Timezone handling — fragile
const utcString = now.toISOString();
const localString = now.toLocaleString("en-US", { timeZone: "America/New_York" });

// Duration calculation
const start = Date.now();
doWork();
const elapsed = Date.now() - start; // milliseconds, no structure

// Comparing dates
const isAfter = dateA.getTime() > dateB.getTime();
```

## After

```typescript
// Creating dates — clear, unambiguous types
const now = Temporal.Now.plainDateTimeISO();
const today = Temporal.Now.plainDateISO();
const instant = Temporal.Now.instant();

// Date arithmetic — readable, no magic numbers
const tomorrow = today.add({ days: 1 });
const nextWeek = today.add({ weeks: 1 });

// Formatting — built-in ISO output
const formatted = today.toString(); // "2020-01-01"
const inTwoDays = today.add({ days: 2 });

// Timezone handling — first-class support
const zonedNow = Temporal.Now.zonedDateTimeISO("America/New_York");
const utcInstant = Temporal.Now.instant();
const tokyoTime = utcInstant.toZonedDateTimeISO("Asia/Tokyo");

// Duration — structured and composable
const start = Temporal.Now.instant();
doWork();
const elapsed = start.until(Temporal.Now.instant());
console.log(elapsed.total("milliseconds"));

// Comparing dates — dedicated methods
const isAfter = Temporal.PlainDate.compare(dateA, dateB) > 0;
```

## Conditions

- Requires `lib: ["esnext"]` or `lib: ["esnext.temporal"]` in tsconfig.json
- Runtime support is still rolling out — verify target environment (Node 22+, modern browsers)
- Replace date libraries (moment, dayjs, date-fns) gradually; start with new code
- `Temporal` objects are immutable — all operations return new instances
- `Temporal.PlainDate` has no time component; `Temporal.PlainDateTime` has no timezone; `Temporal.ZonedDateTime` is fully qualified
