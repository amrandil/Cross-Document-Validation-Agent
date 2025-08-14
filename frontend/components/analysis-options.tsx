"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

export function AnalysisOptions() {
  const [confidenceThreshold, setConfidenceThreshold] = useState([0.7]);
  // Detailed analysis is always enabled; no switch

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
            <span className="font-medium text-microclear-blue">
              {confidenceThreshold[0].toFixed(1)}
            </span>
            <span>1.0</span>
          </div>
          <p className="text-xs text-gray-500">
            Minimum confidence level for fraud detection alerts
          </p>
        </div>

        {/* Detailed analysis switch removed; always enabled */}
      </div>
    </div>
  );
}
