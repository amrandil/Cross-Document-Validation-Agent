"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RefreshCw, Bot, AlertCircle, Settings, Check, X } from "lucide-react";
import { useAgentInfo } from "@/hooks/use-api";
import { fraudDetectionApi } from "@/lib/api";

const AVAILABLE_MODELS = [
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-4o-mini", label: "GPT-4o Mini" },
  { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
  { value: "gpt-4", label: "GPT-4" },
  { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  { value: "custom", label: "Custom Model" },
];

export function AgentInfo() {
  const { data: agentInfo, loading, error, fetchAgentInfo } = useAgentInfo();
  const [isEditing, setIsEditing] = useState(false);
  const [modelConfigs, setModelConfigs] = useState<Record<string, string>>({});
  const [customModels, setCustomModels] = useState<Record<string, string>>({});
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);

  useEffect(() => {
    const loadAgentInfo = async () => {
      try {
        await fetchAgentInfo();
      } catch (err) {
        console.error("Failed to load agent info on mount:", err);
      }
    };
    loadAgentInfo();
  }, [fetchAgentInfo]);

  // Initialize model configs when agent info loads
  useEffect(() => {
    if (agentInfo?.llms_used && !isEditing) {
      const configs: Record<string, string> = {};
      agentInfo.llms_used.forEach((llm) => {
        const key = llm.role.toLowerCase().replace(/\s+/g, "_");
        configs[key] = llm.name;
      });
      setModelConfigs(configs);
    }
  }, [agentInfo, isEditing]);

  const updateModels = async () => {
    setUpdateLoading(true);
    setUpdateError(null);

    try {
      // Build payload with only changed models
      const payload: Record<string, string> = {};

      // Add models from dropdown selections
      Object.keys(modelConfigs).forEach((key) => {
        const value = modelConfigs[key];
        if (value && value.trim()) {
          payload[key] = value.trim();
        }
      });

      // Replace with custom model names (override dropdown selections)
      Object.keys(customModels).forEach((key) => {
        const value = customModels[key];
        if (value && value.trim()) {
          payload[key] = value.trim();
        }
      });

      // Ensure we have something to update
      if (Object.keys(payload).length === 0) {
        setUpdateError(
          "No models selected for update. Please select a model or enter a custom model name."
        );
        return;
      }

      const result = await fraudDetectionApi.updateAgentModels(payload);

      await fetchAgentInfo(); // Refresh the info
      setIsEditing(false);
      setCustomModels({});
    } catch (err) {
      setUpdateError(
        err instanceof Error ? err.message : "Failed to update models"
      );
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleModelChange = (role: string, value: string) => {
    if (value === "custom") {
      // Initialize custom input for this role
      setCustomModels((prev) => ({ ...prev, [role]: "" }));
      return;
    }
    setModelConfigs((prev) => ({ ...prev, [role]: value }));
    // Remove from custom models when selecting a predefined model
    setCustomModels((prev) => {
      const updated = { ...prev };
      delete updated[role];
      return updated;
    });
  };

  const handleCustomModelChange = (role: string, value: string) => {
    setCustomModels((prev) => ({ ...prev, [role]: value }));
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setUpdateError(null);
    setCustomModels({});
    // Reset to original configs
    if (agentInfo?.llms_used) {
      const configs: Record<string, string> = {};
      agentInfo.llms_used.forEach((llm) => {
        const key = llm.role.toLowerCase().replace(/\s+/g, "_");
        configs[key] = llm.name;
      });
      setModelConfigs(configs);
    }
  };

  if (error) {
    return (
      <Alert variant="destructive" className="text-xs">
        <AlertCircle className="h-3 w-3" />
        <AlertDescription className="text-xs">
          <div className="space-y-1">
            <p>{error}</p>
            <Button
              onClick={fetchAgentInfo}
              variant="outline"
              size="sm"
              className="h-6 text-xs"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  if (!agentInfo && !loading) {
    return (
      <div className="text-xs text-gray-600">
        <div className="flex items-center mb-2">
          <Bot className="h-4 w-4 mr-2 text-gray-400" />
          <span className="font-medium">No Agent Info</span>
        </div>
        <Button
          onClick={fetchAgentInfo}
          variant="outline"
          size="sm"
          className="h-6 text-xs"
        >
          <RefreshCw className="h-3 w-3 mr-1" />
          Load Info
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-700">Overview</span>
        <div className="flex items-center space-x-1">
          {!isEditing && (
            <Button
              onClick={() => setIsEditing(true)}
              variant="outline"
              size="sm"
              className="h-6 w-6 p-0"
              title="Edit Models"
            >
              <Settings className="h-3 w-3" />
            </Button>
          )}
          <Button
            onClick={fetchAgentInfo}
            disabled={loading}
            variant="outline"
            size="sm"
            className="h-6 w-6 p-0"
          >
            <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {loading && (
        <div className="text-xs text-gray-600 flex items-center">
          <RefreshCw className="h-3 w-3 animate-spin text-microclear-blue mr-2" />
          Loading...
        </div>
      )}

      {updateError && (
        <Alert variant="destructive" className="text-xs">
          <AlertCircle className="h-3 w-3" />
          <AlertDescription className="text-xs">{updateError}</AlertDescription>
        </Alert>
      )}

      {agentInfo && (
        <div className="space-y-4">
          {agentInfo.llms_used && agentInfo.llms_used.length > 0 && (
            <div>
              <div className="text-[11px] font-medium text-gray-900 mb-2 uppercase tracking-wide">
                Language Models
              </div>
              {isEditing ? (
                <div className="space-y-3">
                  {agentInfo.llms_used.map((llm, idx) => {
                    const roleKey = llm.role.toLowerCase().replace(/\s+/g, "_");
                    const currentValue = modelConfigs[roleKey] || llm.name;
                    const hasCustomInput = customModels[roleKey] !== undefined;
                    const isCustom =
                      hasCustomInput ||
                      !AVAILABLE_MODELS.some(
                        (m) => m.value === currentValue && m.value !== "custom"
                      );

                    return (
                      <div key={idx} className="space-y-2">
                        <Label className="text-[10px] font-medium text-gray-700">
                          {llm.role}
                        </Label>

                        <Select
                          value={isCustom ? "custom" : currentValue}
                          onValueChange={(value) =>
                            handleModelChange(roleKey, value)
                          }
                        >
                          <SelectTrigger className="h-7 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {AVAILABLE_MODELS.map((model) => (
                              <SelectItem
                                key={model.value}
                                value={model.value}
                                className="text-xs"
                              >
                                {model.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        {hasCustomInput && (
                          <Input
                            placeholder="Enter model name (e.g., gpt-4-turbo)"
                            value={
                              customModels[roleKey] ||
                              (isCustom ? currentValue : "")
                            }
                            onChange={(e) =>
                              handleCustomModelChange(roleKey, e.target.value)
                            }
                            className="h-7 text-xs"
                          />
                        )}
                      </div>
                    );
                  })}

                  <div className="flex items-center space-x-2 pt-2">
                    <Button
                      onClick={updateModels}
                      disabled={updateLoading}
                      size="sm"
                      className="h-6 px-3 text-xs bg-green-600 hover:bg-green-700"
                    >
                      {updateLoading ? (
                        <RefreshCw className="h-3 w-3 animate-spin" />
                      ) : (
                        <Check className="h-3 w-3" />
                      )}
                    </Button>
                    <Button
                      onClick={cancelEditing}
                      variant="outline"
                      size="sm"
                      className="h-6 px-3 text-xs"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {agentInfo.llms_used.map((llm, idx) => (
                    <div key={idx} className="flex items-start space-x-2">
                      <Bot className="h-3 w-3 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <div className="text-xs font-medium text-gray-900 break-words">
                          {llm.name}
                        </div>
                        <div className="text-[11px] text-gray-600 break-words">
                          {llm.role}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
