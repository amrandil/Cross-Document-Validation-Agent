"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import {
  AlertTriangle,
  CheckCircle,
  FileText,
  ChevronDown,
  Activity,
  Clock,
  Shield,
  Target,
  TrendingUp,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface AnalysisResultsProps {
  result: any
}

export function AnalysisResults({ result }: AnalysisResultsProps) {
  if (!result) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Results</h3>
          <p className="text-gray-500 text-center">Upload and analyze documents first to see detailed results here.</p>
        </CardContent>
      </Card>
    )
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel?.toUpperCase()) {
      case "LOW":
        return "text-green-600 bg-green-100 border-green-200"
      case "MEDIUM":
        return "text-yellow-600 bg-yellow-100 border-yellow-200"
      case "HIGH":
        return "text-orange-600 bg-orange-100 border-orange-200"
      case "CRITICAL":
        return "text-red-600 bg-red-100 border-red-200"
      default:
        return "text-gray-600 bg-gray-100 border-gray-200"
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel?.toUpperCase()) {
      case "LOW":
        return <CheckCircle className="h-5 w-5" />
      case "MEDIUM":
        return <AlertTriangle className="h-5 w-5" />
      case "HIGH":
        return <AlertTriangle className="h-5 w-5" />
      case "CRITICAL":
        return <Shield className="h-5 w-5" />
      default:
        return <Activity className="h-5 w-5" />
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600"
    if (confidence >= 0.6) return "text-yellow-600"
    if (confidence >= 0.4) return "text-orange-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      {/* Quick Status Banner */}
      {result.fraud_analysis && (
        <Card className={cn("border-2", getRiskColor(result.fraud_analysis.risk_level))}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getRiskIcon(result.fraud_analysis.risk_level)}
                <div>
                  <h3 className="text-lg font-semibold">
                    {result.fraud_analysis.fraud_detected ? "Fraud Indicators Detected" : "No Fraud Detected"}
                  </h3>
                  <p className="text-sm opacity-80">
                    Risk Level: {result.fraud_analysis.risk_level} | Confidence:{" "}
                    {(result.fraud_analysis.overall_confidence * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <Badge className={cn("text-sm px-3 py-1", getRiskColor(result.fraud_analysis.risk_level))}>
                {result.fraud_analysis.risk_level}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-microclear-blue" />
              <div>
                <p className="text-sm font-medium text-gray-600">Bundle ID</p>
                <p className="text-2xl font-bold text-gray-900">{result.bundle_id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-microclear-orange" />
              <div>
                <p className="text-sm font-medium text-gray-600">Documents</p>
                <p className="text-2xl font-bold text-gray-900">{result.documents_processed}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Processing Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {result.processing_time_ms < 1000
                    ? `${result.processing_time_ms}ms`
                    : `${(result.processing_time_ms / 1000).toFixed(1)}s`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium text-gray-600">Status</p>
                {result.fraud_analysis ? (
                  <Badge className={cn("text-sm mt-1", getRiskColor(result.fraud_analysis.risk_level))}>
                    {result.fraud_analysis.fraud_detected ? "DETECTED" : "CLEAR"}
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="mt-1">
                    Processing
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Fraud Analysis */}
      {result.fraud_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-microclear-blue flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Fraud Analysis Report
            </CardTitle>
            <CardDescription>Comprehensive fraud detection analysis and risk assessment</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Risk Assessment Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div
                  className={cn(
                    "text-3xl font-bold mb-2",
                    getRiskColor(result.fraud_analysis.risk_level).split(" ")[0],
                  )}
                >
                  {result.fraud_analysis.risk_level}
                </div>
                <p className="text-sm text-gray-600">Risk Level</p>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div
                  className={cn(
                    "text-3xl font-bold mb-2",
                    getConfidenceColor(result.fraud_analysis.overall_confidence),
                  )}
                >
                  {(result.fraud_analysis.overall_confidence * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">Confidence Score</p>
                <Progress value={result.fraud_analysis.overall_confidence * 100} className="mt-2 h-2" />
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-3xl font-bold mb-2 text-microclear-blue">
                  {result.fraud_analysis.investigation_priority}
                </div>
                <p className="text-sm text-gray-600">Investigation Priority</p>
              </div>
            </div>

            <Separator />

            {/* Executive Summary */}
            {result.fraud_analysis.executive_summary && (
              <div>
                <h4 className="font-semibold mb-3 text-microclear-blue">Executive Summary</h4>
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                  <p className="text-gray-800 leading-relaxed">{result.fraud_analysis.executive_summary}</p>
                </div>
              </div>
            )}

            {/* Recommended Actions */}
            {result.fraud_analysis.recommended_actions && result.fraud_analysis.recommended_actions.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3 text-microclear-blue">Recommended Actions</h4>
                <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg">
                  <ul className="space-y-2">
                    {result.fraud_analysis.recommended_actions.map((action: string, index: number) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-microclear-orange rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-800">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Raw Analysis Data Toggle */}
            <Collapsible>
              <CollapsibleTrigger asChild>
                <Button variant="outline" className="w-full bg-transparent">
                  <ChevronDown className="h-4 w-4 mr-2" />
                  View Raw Analysis Data
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-4">
                <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify(result.fraud_analysis, null, 2)}
                </pre>
              </CollapsibleContent>
            </Collapsible>
          </CardContent>
        </Card>
      )}

      {/* Agent Execution Trace */}
      {result.agent_execution && (
        <Card>
          <CardHeader>
            <CardTitle className="text-microclear-blue flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              Agent Execution Trace
            </CardTitle>
            <CardDescription>Detailed step-by-step investigation process and reasoning</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Execution Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">{result.agent_execution.execution_id}</div>
                <div className="text-sm text-gray-600">Execution ID</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">{result.agent_execution.total_steps}</div>
                <div className="text-sm text-gray-600">Investigation Steps</div>
              </div>
              <div className="text-center">
                <Badge
                  variant={result.agent_execution.status === "completed" ? "default" : "secondary"}
                  className="text-sm"
                >
                  {result.agent_execution.status.toUpperCase()}
                </Badge>
                <div className="text-sm text-gray-600 mt-1">Execution Status</div>
              </div>
            </div>

            {/* Investigation Steps */}
            {result.agent_execution.steps && result.agent_execution.steps.length > 0 && (
              <div>
                <h4 className="font-semibold mb-4 text-microclear-blue">Investigation Steps</h4>
                <div className="space-y-3">
                  {result.agent_execution.steps.map((step: any, index: number) => (
                    <Collapsible key={index}>
                      <CollapsibleTrigger asChild>
                        <Button
                          variant="ghost"
                          className="w-full justify-between p-4 h-auto border border-gray-200 hover:border-microclear-blue"
                        >
                          <div className="text-left flex items-center space-x-3">
                            <div className="w-8 h-8 bg-microclear-blue text-white rounded-full flex items-center justify-center text-sm font-bold">
                              {step.step_number}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900">
                                {step.step_type.replace("_", " ").replace(/\b\w/g, (l: string) => l.toUpperCase())}
                              </div>
                              <div className="text-sm text-gray-500 truncate max-w-md">{step.content}</div>
                            </div>
                          </div>
                          <ChevronDown className="h-4 w-4 text-gray-400" />
                        </Button>
                      </CollapsibleTrigger>
                      <CollapsibleContent className="px-4 pb-4 border-l-2 border-microclear-blue ml-4">
                        <div className="space-y-4 text-sm pl-8">
                          <div className="bg-white p-3 rounded border">
                            <strong className="text-microclear-blue">Analysis:</strong>
                            <p className="mt-1 text-gray-700">{step.content}</p>
                          </div>

                          {step.tool_used && (
                            <div className="bg-blue-50 p-3 rounded border border-blue-200">
                              <strong className="text-microclear-blue">Tool Used:</strong>
                              <Badge variant="secondary" className="ml-2">
                                {step.tool_used}
                              </Badge>
                            </div>
                          )}

                          {step.tool_output && (
                            <div className="bg-gray-50 p-3 rounded border">
                              <strong className="text-microclear-blue">Tool Output:</strong>
                              <pre className="mt-2 p-2 bg-white rounded text-xs overflow-x-auto border max-h-40">
                                {step.tool_output}
                              </pre>
                            </div>
                          )}

                          <div className="text-xs text-gray-500 flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            <strong>Timestamp:</strong> {new Date(step.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </CollapsibleContent>
                    </Collapsible>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
