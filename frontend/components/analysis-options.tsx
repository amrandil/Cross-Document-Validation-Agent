"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

export function AnalysisOptions() {
  const [confidenceThreshold, setConfidenceThreshold] = useState([0.7]);
  // Detailed analysis is always enabled; no switch

  return (
    <div className="space-y-3">
      <Label htmlFor="confidence-threshold" className="text-xs font-medium">
        Confidence Threshold
      </Label>
      <Slider
        id="confidence-threshold"
        min={0}
        max={1}
        step={0.1}
        value={confidenceThreshold}
        onValueChange={setConfidenceThreshold}
        className="w-full"
      />
      <div className="flex justify-between text-[10px] text-gray-500">
        <span>0.0</span>
        <span className="font-medium text-microclear-blue">
          {confidenceThreshold[0].toFixed(1)}
        </span>
        <span>1.0</span>
      </div>
      <p className="text-[11px] text-gray-500">
        Sets the minimum confidence to raise an alert
      </p>
    </div>
  );
}
