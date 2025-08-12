"use client"

import type React from "react"

import { useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import {
  RefreshCw,
  Bot,
  PenToolIcon as Tool,
  FileText,
  Shield,
  AlertCircle,
  CheckCircle,
  Info,
  Zap,
  Database,
  AlertTriangle,
} from "lucide-react"
import { useAgentInfo } from "@/hooks/use-api"

interface AgentCapability {
  name: string
  description: string
  icon: React.ReactNode
}

export function AgentInfo() {
  const { data: agentInfo, loading, error, fetchAgentInfo } = useAgentInfo()

  useEffect(() => {
    const loadAgentInfo = async () => {
      try {
        await fetchAgentInfo()
      } catch (err) {
        console.error("Failed to load agent info on mount:", err)
      }
    }
    loadAgentInfo()
  }, [fetchAgentInfo])

  const getCapabilityIcon = (capability: string) => {
    const lowerCapability = capability.toLowerCase()
    if (lowerCapability.includes("document")) return <FileText className="h-4 w-4" />
    if (lowerCapability.includes("fraud")) return <Shield className="h-4 w-4" />
    if (lowerCapability.includes("analysis")) return <Zap className="h-4 w-4" />
    if (lowerCapability.includes("data")) return <Database className="h-4 w-4" />
    return <Tool className="h-4 w-4" />
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-2">
            <p>{error}</p>
            {error.includes("Backend server") && (
              <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                <p>
                  <strong>To fix this:</strong>
                </p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Start your LangChain backend server</li>
                  <li>Ensure it's running on http://localhost:8000</li>
                  <li>Click the retry button below</li>
                </ol>
              </div>
            )}
            <Button onClick={fetchAgentInfo} variant="outline" size="sm" className="ml-0 mt-2 bg-transparent">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    )
  }

  if (!agentInfo && !loading) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Bot className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Agent Information</h3>
          <p className="text-gray-500 text-center mb-4">Click refresh to load agent capabilities and information.</p>
          <Button onClick={fetchAgentInfo} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Load Agent Info
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-microclear-blue">Agent Information</h2>
          <p className="text-gray-600">Fraud detection agent capabilities and configuration</p>
        </div>
        <Button onClick={fetchAgentInfo} disabled={loading} variant="outline" size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {loading && (
        <Card>
          <CardContent className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-microclear-blue mr-2" />
            <span>Loading agent information...</span>
          </CardContent>
        </Card>
      )}

      {agentInfo && (
        <div className="space-y-6">
          {/* Agent Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-microclear-blue">
                <Bot className="h-5 w-5 mr-2" />
                Agent Overview
              </CardTitle>
              <CardDescription>Core agent specifications and capabilities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <Bot className="h-8 w-8 text-microclear-blue mx-auto mb-2" />
                  <p className="text-sm text-gray-600 mb-1">Agent Type</p>
                  <p className="font-semibold text-gray-900">
                    {agentInfo.agent_type?.replace("_", " ").replace(/\b\w/g, (l: string) => l.toUpperCase()) ||
                      "Multi-Document Fraud Detection"}
                  </p>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <Tool className="h-8 w-8 text-microclear-orange mx-auto mb-2" />
                  <p className="text-sm text-gray-600 mb-1">Available Tools</p>
                  <p className="font-semibold text-gray-900">{agentInfo.tools_count || agentInfo.tools?.length || 0}</p>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <FileText className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600 mb-1">Document Types</p>
                  <p className="font-semibold text-gray-900">
                    {agentInfo.supported_document_types?.length || "Multiple"}
                  </p>
                </div>

                <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
                  <Shield className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600 mb-1">Fraud Types</p>
                  <p className="font-semibold text-gray-900">{agentInfo.fraud_types_detected?.length || "Multiple"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Document Types Support */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-microclear-blue">
                <FileText className="h-5 w-5 mr-2" />
                Supported Document Types
              </CardTitle>
              <CardDescription>Document formats and types that can be analyzed for fraud detection</CardDescription>
            </CardHeader>
            <CardContent>
              {agentInfo.supported_document_types && agentInfo.supported_document_types.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {agentInfo.supported_document_types.map((type: string) => (
                    <div key={type} className="flex items-center p-3 bg-gray-50 rounded-lg border">
                      <FileText className="h-4 w-4 text-microclear-blue mr-2" />
                      <span className="text-sm font-medium">
                        {type.replace("_", " ").replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">
                    Document type information not available. The agent supports common customs document formats.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Fraud Detection Capabilities */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-microclear-blue">
                <Shield className="h-5 w-5 mr-2" />
                Fraud Detection Capabilities
              </CardTitle>
              <CardDescription>Types of fraud patterns and schemes the agent can identify</CardDescription>
            </CardHeader>
            <CardContent>
              {agentInfo.fraud_types_detected && agentInfo.fraud_types_detected.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {agentInfo.fraud_types_detected.map((type: string) => (
                    <div key={type} className="flex items-center p-3 bg-red-50 rounded-lg border border-red-200">
                      <AlertTriangle className="h-4 w-4 text-red-600 mr-2" />
                      <span className="text-sm font-medium text-red-800">
                        {type.replace("_", " ").replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">
                    Fraud type information not available. The agent can detect various customs fraud patterns.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Available Tools */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-microclear-blue">
                <Tool className="h-5 w-5 mr-2" />
                Available Analysis Tools
              </CardTitle>
              <CardDescription>Tools and capabilities available to the fraud detection agent</CardDescription>
            </CardHeader>
            <CardContent>
              {agentInfo.tools && agentInfo.tools.length > 0 ? (
                <div className="space-y-3">
                  {agentInfo.tools.map((tool: string, index: number) => (
                    <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg border hover:bg-gray-100">
                      {getCapabilityIcon(tool)}
                      <div className="ml-3">
                        <span className="text-sm font-medium text-gray-900">{tool}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Tool className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Tool information not available from the agent.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Agent Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-microclear-blue">
                <CheckCircle className="h-5 w-5 mr-2" />
                Agent Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <div>
                    <p className="font-medium text-green-800">Agent Online</p>
                    <p className="text-sm text-green-600">Ready to analyze documents for fraud detection</p>
                  </div>
                </div>
                <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
              </div>

              <Separator className="my-4" />

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="font-medium">{new Date().toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">API Version</p>
                  <p className="font-medium">v1</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Raw Agent Data (for debugging) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-gray-600">
                <Info className="h-5 w-5 mr-2" />
                Raw Agent Data
              </CardTitle>
              <CardDescription>Complete agent information for debugging purposes</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto max-h-64">
                {JSON.stringify(agentInfo, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
