"use client"

import { useState, useCallback } from "react"
import { fraudDetectionApi, ApiError } from "@/lib/api"
import type { AnalysisRequest, AnalysisResponse, HealthResponse, AgentInfoResponse } from "@/lib/api"

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useHealthCheck() {
  const [state, setState] = useState<ApiState<HealthResponse>>({
    data: null,
    loading: false,
    error: null,
  })

  const checkHealth = useCallback(async () => {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await fraudDetectionApi.checkHealth()
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to check API health"
      setState({ data: null, loading: false, error: errorMessage })
      console.error("Health check failed:", error)
      return null
    }
  }, [])

  return {
    ...state,
    checkHealth,
  }
}

export function useAgentInfo() {
  const [state, setState] = useState<ApiState<AgentInfoResponse>>({
    data: null,
    loading: false,
    error: null,
  })

  const fetchAgentInfo = useCallback(async () => {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await fraudDetectionApi.getAgentInfo()
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to fetch agent information"
      setState({ data: null, loading: false, error: errorMessage })
      console.error("Agent info fetch failed:", error)
      return null
    }
  }, [])

  return {
    ...state,
    fetchAgentInfo,
  }
}

export function useDocumentAnalysis() {
  const [state, setState] = useState<ApiState<AnalysisResponse>>({
    data: null,
    loading: false,
    error: null,
  })

  const analyzeDocuments = useCallback(async (request: AnalysisRequest) => {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await fraudDetectionApi.analyzeDocuments(request)
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to analyze documents"
      setState({ data: null, loading: false, error: errorMessage })
      console.error("Document analysis failed:", error)
      return null
    }
  }, [])

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    analyzeDocuments,
    reset,
  }
}

// Generic API hook for custom operations
export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setState({ data: null, loading: true, error: null })
    try {
      const data = await apiCall()
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "API request failed"
      setState({ data: null, loading: false, error: errorMessage })
      console.error("API call failed:", error)
      return null
    }
  }, [])

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    execute,
    reset,
  }
}
