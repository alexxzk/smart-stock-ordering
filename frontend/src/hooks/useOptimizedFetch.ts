import { useState, useEffect, useCallback, useRef } from 'react';

interface UseOptimizedFetchOptions<T> {
  url: string;
  dependencies?: any[];
  cacheTime?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

interface UseOptimizedFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  clearCache: () => void;
}

// Simple in-memory cache
const cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

export function useOptimizedFetch<T>({
  url,
  dependencies = [],
  cacheTime = 60000, // 1 minute default
  retryAttempts = 3,
  retryDelay = 1000
}: UseOptimizedFetchOptions<T>): UseOptimizedFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);

  const clearCache = useCallback(() => {
    cache.delete(url);
  }, [url]);

  const fetchData = useCallback(async (isRetry = false) => {
    // Check cache first
    const cached = cache.get(url);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      setData(cached.data);
      setLoading(false);
      setError(null);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(url, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Cache the result
      cache.set(url, {
        data: result,
        timestamp: Date.now(),
        ttl: cacheTime
      });

      setData(result);
      setLoading(false);
      retryCountRef.current = 0; // Reset retry count on success
    } catch (err: any) {
      if (err.name === 'AbortError') {
        return; // Request was cancelled
      }

      console.error('Fetch error:', err);
      
      // Retry logic
      if (!isRetry && retryCountRef.current < retryAttempts) {
        retryCountRef.current++;
        setTimeout(() => {
          fetchData(true);
        }, retryDelay);
        return;
      }

      setError(err.message || 'An error occurred');
      setLoading(false);
      retryCountRef.current = 0;
    }
  }, [url, cacheTime, retryAttempts, retryDelay]);

  const refetch = useCallback(() => {
    clearCache();
    fetchData();
  }, [clearCache, fetchData]);

  useEffect(() => {
    fetchData();
    
    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData, ...dependencies]);

  return {
    data,
    loading,
    error,
    refetch,
    clearCache
  };
} 