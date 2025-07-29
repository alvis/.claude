# Performance Optimization

## Frontend Performance (React/Next.js)

See `06-react-conventions.md` for React-specific performance optimization techniques including:
- Component memoization strategies
- State management optimization
- Code splitting with dynamic imports
- Next.js Image and Font optimization

### Bundle Optimization

#### Tree Shaking

```typescript
// ✅ Named imports for better tree shaking
import { debounce } from 'lodash-es';

// ❌ Avoid default imports of large libraries
import _ from 'lodash';

// ✅ Import only what you need
import debounce from 'lodash-es/debounce';
```

#### Bundle Analysis

```json
// package.json scripts
{
  "scripts": {
    "analyze": "ANALYZE=true next build",
    "analyze:server": "BUNDLE_ANALYZE=server next build",
    "analyze:browser": "BUNDLE_ANALYZE=browser next build"
  }
}
```

## Backend Performance (Node.js)

### Database Optimization

#### Query Optimization

```typescript
// ✅ Use select to limit fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    email: true,
    // Don't select passwordHash, etc.
  },
});

// ✅ Use includes wisely
const userWithPosts = await prisma.user.findUnique({
  where: { id },
  include: {
    posts: {
      take: 10, // Limit related data
      orderBy: { createdAt: 'desc' },
    },
  },
});

// ✅ Use indexes (in Prisma schema)
model User {
  id    String @id @default(uuid())
  email String @unique
  name  String
  
  @@index([email, name]) // Composite index
}
```

#### Connection Pooling

```typescript
// Configure Prisma connection pool
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Connection pool settings
  connectionLimit: 10,
});

// Reuse Prisma client instance
export const db = global.prisma || prisma;

if (process.env.NODE_ENV !== 'production') {
  global.prisma = db;
}
```

### Caching Strategies

#### In-Memory Caching

```typescript
// ✅ Simple in-memory cache
const cache = new Map<string, { data: any; expires: number }>();

export function getCached<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 5 * 60 * 1000 // 5 minutes
): Promise<T> {
  const cached = cache.get(key);
  
  if (cached && cached.expires > Date.now()) {
    return Promise.resolve(cached.data);
  }
  
  return fetcher().then(data => {
    cache.set(key, { data, expires: Date.now() + ttl });
    return data;
  });
}

// ✅ Redis caching for distributed systems
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export async function getCachedRedis<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 300 // seconds
): Promise<T> {
  const cached = await redis.get(key);
  
  if (cached) {
    return JSON.parse(cached);
  }
  
  const data = await fetcher();
  await redis.setex(key, ttl, JSON.stringify(data));
  return data;
}
```

#### HTTP Caching

```typescript
// ✅ Set appropriate cache headers
export function setCacheControl(res: Response, maxAge: number = 3600) {
  res.setHeader('Cache-Control', `public, max-age=${maxAge}, s-maxage=${maxAge}`);
}

// ✅ Use ETags for conditional requests
import etag from 'etag';

export function handleETag(req: Request, res: Response, data: any): boolean {
  const etagValue = etag(JSON.stringify(data));
  res.setHeader('ETag', etagValue);
  
  if (req.headers['if-none-match'] === etagValue) {
    res.status(304).end();
    return true;
  }
  
  return false;
}
```

### Async Operation Optimization

#### Parallel Processing

```typescript
// ✅ Run independent operations in parallel
const [user, posts, comments] = await Promise.all([
  getUser(userId),
  getUserPosts(userId),
  getUserComments(userId),
]);

// ❌ Avoid sequential operations
const user = await getUser(userId);
const posts = await getUserPosts(userId);
const comments = await getUserComments(userId);

// ✅ Use Promise.allSettled for fault tolerance
const results = await Promise.allSettled([
  fetchPrimaryData(),
  fetchSecondaryData(), // Won't fail if this fails
  fetchOptionalData(),
]);
```

#### Stream Processing

```typescript
// ✅ Use streams for large data
import { pipeline } from 'stream/promises';

export async function processLargeFile(filePath: string) {
  await pipeline(
    fs.createReadStream(filePath),
    new Transform({
      transform(chunk, encoding, callback) {
        // Process chunk
        callback(null, processedChunk);
      },
    }),
    fs.createWriteStream(outputPath)
  );
}

// ✅ Stream database results
const stream = prisma.user.findMany({
  cursor: { id: lastId },
  take: 100,
}).stream();

for await (const users of stream) {
  await processBatch(users);
}
```

## Memory Management

### Prevent Memory Leaks

```typescript
// ✅ Clean up event listeners
class Component {
  private listener: (() => void) | null = null;
  
  mount() {
    this.listener = () => action.log.debug('event');
    window.addEventListener('resize', this.listener);
  }
  
  unmount() {
    if (this.listener) {
      window.removeEventListener('resize', this.listener);
      this.listener = null;
    }
  }
}

// ✅ Clear timers
const timer = setTimeout(() => {
  // do something
}, 1000);

// Clean up
clearTimeout(timer);

// ✅ Limit cache size
class LRUCache<T> {
  private cache = new Map<string, T>();
  private maxSize: number;
  
  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }
  
  set(key: string, value: T) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}
```

## Monitoring & Profiling

### Performance Monitoring

```typescript
// ✅ Measure operation time
export async function measurePerformance<T>(
  name: string,
  operation: () => Promise<T>
): Promise<T> {
  const start = performance.now();
  
  try {
    const result = await operation();
    const duration = performance.now() - start;
    
    if (duration > 1000) {
      action.log.warn('slow operation detected', { name, duration });
    }
    
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    action.log.error('operation failed', { name, duration, error });
    throw error;
  }
}

// Usage
const data = await measurePerformance('fetchUserData', () => 
  fetchUserData(userId)
);
```

### Resource Monitoring

```typescript
// Monitor memory usage
// monitor memory usage in service context
export function monitorMemory(action: Action) {
  setInterval(() => {
    const usage = process.memoryUsage();
    action.log.info('memory usage', {
      rss: Math.round(usage.rss / 1024 / 1024),
      heapTotal: Math.round(usage.heapTotal / 1024 / 1024),
      heapUsed: Math.round(usage.heapUsed / 1024 / 1024),
      unit: 'MB',
    });
  }, 60000); // every minute
}
```

## Web Vitals

### Core Web Vitals Targets

- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Optimization Techniques

```typescript
// ✅ Preload critical resources
<link rel="preload" href="/fonts/main.woff2" as="font" crossOrigin="" />
<link rel="preconnect" href="https://api.example.com" />

// ✅ Lazy load below-fold content
const LazySection = dynamic(() => import('#components/Section'), {
  ssr: false,
});

// ✅ Optimize Critical CSS
// Use CSS-in-JS or CSS Modules for automatic critical CSS
```

## Best Practices Summary

1. **Measure First** - Profile before optimizing
2. **Optimize Critical Path** - Focus on user-facing performance
3. **Cache Aggressively** - But invalidate correctly
4. **Load Progressively** - Prioritize above-fold content
5. **Monitor Continuously** - Set up performance budgets

--- END ---