"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AlertTriangle, CheckCircle, Shield, TrendingUp, Clock, FileText } from "lucide-react"
import { cn } from "@/lib/utils"

interface AnalysisSummaryProps {
  result: any
}

export function AnalysisSummary({ result }: AnalysisSummaryProps) {
  if (!result) return null

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel?.toUpperCase()) {
      case "LOW":
        return "text-green-600 bg-green-100"
      case "MEDIUM":
        return "text-yellow-600 bg-yellow-100"
      case "HIGH":
        return "text-orange-600 bg-orange-100"
      case "CRITICAL":
        return "text-red-600 bg-red-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel?.toUpperCase()) {
      case "LOW":
        return <CheckCircle className="h-5 w-5" />
      case "MEDIUM":
      case "HIGH":
      case "CRITICAL":
        return <AlertTriangle className="h-5 w-5" />
      default:
        return <Shield className="h-5 w-5" />
    }
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-microclear-blue">Quick Analysis Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <FileText className="h-8 w-8 text-microclear-blue" />
            <div>
              <p className="text-sm text-gray-600">Bundle</p>
              <p className="font-semibold">{result.bundle_id}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <TrendingUp className="h-8 w-8 text-microclear-orange" />
            <div>
              <p className="text-sm text-gray-600">Documents</p>
              <p className="font-semibold">{result.documents_processed}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <Clock className="h-8 w-8 text-gray-500" />
            <div>
              <p className="text-sm text-gray-600">Time</p>
              <p className="font-semibold">{result.processing_time_ms}ms</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            {result.fraud_analysis && getRiskIcon(result.fraud_analysis.risk_level)}
            <div>
              <p className="text-sm text-gray-600">Status</p>
              {result.fraud_analysis ? (
                <Badge className={cn("text-xs", getRiskColor(result.fraud_analysis.risk_level))}>
                  {result.fraud_analysis.fraud_detected ? "DETECTED" : "CLEAR"}
                </Badge>
              ) : (
                <Badge variant="secondary">Processing</Badge>
              )}
            </div>
          </div>
        </div>

        {result.fraud_analysis && (
          <div className="mt-6 p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium">Risk Assessment</h4>
              <Badge className={cn(getRiskColor(result.fraud_analysis.risk_level))}>
                {result.fraud_analysis.risk_level}
              </Badge>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Confidence Level</span>
                <span className="font-medium">{(result.fraud_analysis.overall_confidence * 100).toFixed(1)}%</span>
              </div>
              <Progress value={result.fraud_analysis.overall_confidence * 100} className="h-2" />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
