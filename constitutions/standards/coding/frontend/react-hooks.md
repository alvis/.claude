# React Hooks Standards

_Standards for custom hooks design, patterns, and best practices_

## Hook Design Principles

### Core Rules

- **Start with `use` prefix** - All custom hooks must begin with "use"
- **Return consistent interface** - Maintain predictable return patterns
- **Handle loading and error states** - Always consider async operations
- **Make hooks reusable and composable** - Design for multiple use cases
- **Follow dependency rules** - Properly handle dependencies in useEffect/useMemo

### Hook Naming

```typescript
// ✅ GOOD: clear, descriptive hook names
useUserData(userId: string)
useApiRequest<T>(url: string)
useLocalStorage(key: string)
useDebounced(value: string, delay: number)
useAuth()
usePermissions(userId: string)

// ❌ BAD: unclear or non-hook names
getUserData(userId: string)  // Missing 'use' prefix
useData()                    // Too generic
useStuff()                   // Not descriptive
```

## Hook Template Pattern

### Standard Hook Structure

```typescript
interface UseDataOptions {
  enabled?: boolean;
  refetchOnMount?: boolean;
  retryCount?: number;
}

interface UseDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  isValidating: boolean;
}

export function useData<T>(
  url: string,
  options: UseDataOptions = {},
): UseDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const refetch = useCallback(async () => {
    if (!options.enabled) return;

    setLoading(true);
    setError(null);
    setIsValidating(true);

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
      setIsValidating(false);
    }
  }, [url, options.enabled]);

  useEffect(() => {
    if (options.enabled !== false && options.refetchOnMount !== false) {
      refetch();
    }
  }, [refetch, options.enabled, options.refetchOnMount]);

  return { data, loading, error, refetch, isValidating };
}
```

## Common Hook Patterns

### Data Fetching Hooks

```typescript
// ✅ GOOD: comprehensive data fetching hook
export function useApiQuery<T>(endpoint: string) {
  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiClient.get<T>(endpoint);
      setState({ data: response.data, loading: false, error: null });
    } catch (error) {
      setState({ data: null, loading: false, error: error as Error });
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...state,
    refetch: fetchData,
    isLoading: state.loading,
    isError: state.error !== null,
    isSuccess: state.data !== null && !state.loading && !state.error,
  };
}
```

### Local Storage Hooks

```typescript
// ✅ GOOD: type-safe localStorage hook
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((val: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue],
  );

  return [storedValue, setValue];
}
```

### Debounce Hooks

```typescript
// ✅ GOOD: debounce hook with cleanup
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// ✅ GOOD: debounced callback hook
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
): T {
  const callbackRef = useRef(callback);
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    callbackRef.current = callback;
  });

  return useCallback(
    ((...args) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    }) as T,
    [delay],
  );
}
```

## Advanced Hook Patterns

### Hook Composition

```typescript
// ✅ GOOD: composable hooks
export function useAuth() {
  const [user, setUser] = useLocalStorage<User | null>("user", null);
  const [token, setToken] = useLocalStorage<string | null>("token", null);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const response = await authApi.login(credentials);
      setUser(response.user);
      setToken(response.token);
    },
    [setUser, setToken],
  );

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
  }, [setUser, setToken]);

  return {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!user && !!token,
  };
}

export function usePermissions(userId?: string) {
  const { user, isAuthenticated } = useAuth();
  const effectiveUserId = userId || user?.id;

  const { data: permissions, loading } = useApiQuery<Permission[]>(
    effectiveUserId && isAuthenticated
      ? `/users/${effectiveUserId}/permissions`
      : null,
  );

  const hasPermission = useCallback(
    (permission: string) => {
      return permissions?.some((p) => p.name === permission) ?? false;
    },
    [permissions],
  );

  return {
    permissions: permissions || [],
    loading,
    hasPermission,
    isAdmin: hasPermission("admin"),
    canEdit: hasPermission("edit"),
    canView: hasPermission("view"),
  };
}
```

### Custom Hook with Reducer

```typescript
// ✅ GOOD: complex state management with useReducer
interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

type FormAction<T> =
  | { type: "SET_VALUE"; field: keyof T; value: T[keyof T] }
  | { type: "SET_ERROR"; field: keyof T; error: string }
  | { type: "SET_TOUCHED"; field: keyof T }
  | { type: "SET_SUBMITTING"; isSubmitting: boolean }
  | { type: "RESET"; initialValues: T };

function formReducer<T>(
  state: FormState<T>,
  action: FormAction<T>,
): FormState<T> {
  switch (action.type) {
    case "SET_VALUE":
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
        errors: { ...state.errors, [action.field]: undefined },
      };
    case "SET_ERROR":
      return {
        ...state,
        errors: { ...state.errors, [action.field]: action.error },
        isValid: false,
      };
    case "SET_TOUCHED":
      return {
        ...state,
        touched: { ...state.touched, [action.field]: true },
      };
    case "SET_SUBMITTING":
      return { ...state, isSubmitting: action.isSubmitting };
    case "RESET":
      return {
        values: action.initialValues,
        errors: {},
        touched: {},
        isSubmitting: false,
        isValid: true,
      };
    default:
      return state;
  }
}

export function useForm<T extends Record<string, any>>(
  initialValues: T,
  validationSchema?: (values: T) => Partial<Record<keyof T, string>>,
) {
  const [state, dispatch] = useReducer(formReducer, {
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValid: true,
  } as FormState<T>);

  const setValue = useCallback(
    (field: keyof T, value: T[keyof T]) => {
      dispatch({ type: "SET_VALUE", field, value });

      if (validationSchema) {
        const errors = validationSchema({ ...state.values, [field]: value });
        if (errors[field]) {
          dispatch({ type: "SET_ERROR", field, error: errors[field]! });
        }
      }
    },
    [state.values, validationSchema],
  );

  const setTouched = useCallback((field: keyof T) => {
    dispatch({ type: "SET_TOUCHED", field });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: "RESET", initialValues });
  }, [initialValues]);

  return {
    values: state.values,
    errors: state.errors,
    touched: state.touched,
    isSubmitting: state.isSubmitting,
    isValid: state.isValid,
    setValue,
    setTouched,
    reset,
  };
}
```

## Hook Testing

### Testing Custom Hooks

```typescript
// ✅ GOOD: hook testing with renderHook
import { renderHook, act } from "@testing-library/react";
import { useCounter } from "./useCounter";

describe("useCounter", () => {
  it("should initialize with default value", () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
  });

  it("should initialize with custom value", () => {
    const { result } = renderHook(() => useCounter(10));

    expect(result.current.count).toBe(10);
  });

  it("should increment count", () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("should decrement count", () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });
});
```

## Hook Dependencies

### Dependency Management

```typescript
// ✅ GOOD: proper dependency management
export function useUserData(userId: string) {
  const [userData, setUserData] = useState<User | null>(null);

  // Memoize expensive operations
  const processedData = useMemo(() => {
    if (!userData) return null;
    return {
      ...userData,
      fullName: `${userData.firstName} ${userData.lastName}`,
      initials: `${userData.firstName[0]}${userData.lastName[0]}`,
    };
  }, [userData]);

  // Stable callback reference
  const refreshUser = useCallback(async () => {
    if (!userId) return;

    try {
      const user = await fetchUser(userId);
      setUserData(user);
    } catch (error) {
      console.error("Failed to fetch user:", error);
    }
  }, [userId]);

  // Effect with proper dependencies
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  return {
    userData: processedData,
    refreshUser,
    isLoading: userData === null,
  };
}
```

## Hook Anti-Patterns

### Common Mistakes to Avoid

```typescript
// ❌ BAD: missing dependencies
export function useBadEffect(user: User) {
  useEffect(() => {
    fetchUserData(user.id).then(setData);
  }, []); // Missing user.id dependency
}

// ❌ BAD: creating objects in hook return
export function useBadReturn(data: any[]) {
  return {
    data,
    // New object every render - breaks memoization
    metadata: { count: data.length, lastUpdated: Date.now() },
  };
}

// ❌ BAD: not handling loading/error states
export function useBadApiCall(url: string) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then(setData);
  }, [url]);

  return data; // No loading or error state
}

// ✅ GOOD: proper hook implementation
export function useGoodApiCall(url: string) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) {
          setState({ data, loading: false, error: null });
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setState({ data: null, loading: false, error });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [url]);

  return state;
}
```
