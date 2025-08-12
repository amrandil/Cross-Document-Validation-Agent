"use client"

import { useState } from "react"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function AnalysisOptions() {
  const [confidenceThreshold, setConfidenceThreshold] = useState([0.7])
  const [detailedAnalysis, setDetailedAnalysis] = useState(true)

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-3">
          <Label htmlFor="confidence-threshold" className="text-sm font-medium">
            Confidence Threshold
          </Label>
          <div className="px-2">
            <Slider
              id="confidence-threshold"
              min={0}
              max={1}
              step={0.1}
              value={confidenceThreshold}
              onValueChange={setConfidenceThreshold}
              className="w-full"
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>0.0</span>
            <span className="font-medium text-microclear-blue">{confidenceThreshold[0].toFixed(1)}</span>
            <span>1.0</span>
          </div>
          <p className="text-xs text-gray-500">Minimum confidence level for fraud detection alerts</p>
        </div>

        <div className="flex items-center justify-between space-x-2">
          <div className="space-y-1">
            <Label htmlFor="detailed-analysis" className="text-sm font-medium">
              Detailed Analysis
            </Label>
            <p className="text-xs text-gray-500">Include step-by-step agent reasoning</p>
          </div>
          <Switch id="detailed-analysis" checked={detailedAnalysis} onCheckedChange={setDetailedAnalysis} />
        </div>
      </div>

      <Card className="bg-blue-50 border-microclear-blue">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-microclear-blue">Analysis Settings</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">Confidence:</span>
              <span className="font-medium">{(confidenceThreshold[0] * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Detailed Mode:</span>
              <span className="font-medium">{detailedAnalysis ? "Enabled" : "Disabled"}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
