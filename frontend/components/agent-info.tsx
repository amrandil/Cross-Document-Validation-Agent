"use client";

import type React from "react";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
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
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useAgentInfo } from "@/hooks/use-api";

interface AgentCapability {
  name: string;
  description: string;
  icon: React.ReactNode;
}

export function AgentInfo() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { data: agentInfo, loading, error, fetchAgentInfo } = useAgentInfo();

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

  const getCapabilityIcon = (capability: string) => {
    const lowerCapability = capability.toLowerCase();
    if (lowerCapability.includes("document"))
      return <FileText className="h-3 w-3" />;
    if (lowerCapability.includes("fraud"))
      return <Shield className="h-3 w-3" />;
    if (lowerCapability.includes("analysis"))
      return <Zap className="h-3 w-3" />;
    if (lowerCapability.includes("data"))
      return <Database className="h-3 w-3" />;
    return <Tool className="h-3 w-3" />;
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
      <Card className="text-xs">
        <CardContent className="flex flex-col items-center justify-center py-4">
          <Bot className="h-6 w-6 text-gray-400 mb-2" />
          <h3 className="text-sm font-medium text-gray-900 mb-1">
            No Agent Info
          </h3>
          <Button
            onClick={fetchAgentInfo}
            variant="outline"
            size="sm"
            className="h-6 text-xs"
          >
            <RefreshCw className="h-3 w-3 mr-1" />
            Load Info
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-700">Agent Overview</span>
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

      {loading && (
        <Card className="text-xs">
          <CardContent className="flex items-center justify-center py-3">
            <RefreshCw className="h-4 w-4 animate-spin text-microclear-blue mr-2" />
            <span>Loading...</span>
          </CardContent>
        </Card>
      )}

      {agentInfo && (
        <Card className="text-xs">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center text-sm">
              <Bot className="h-4 w-4 mr-1" />
              LLMs Used
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {agentInfo.llms_used && agentInfo.llms_used.length > 0 ? (
              <div className="space-y-1">
                {agentInfo.llms_used.map((m: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-start p-2 bg-gray-50 rounded border text-xs"
                    title={`${m.name} (${m.role})`}
                  >
                    <Bot className="h-3 w-3 text-microclear-blue mt-0.5 mr-2" />
                    <div className="min-w-0">
                      <div className="font-medium break-words">{m.name}</div>
                      <div className="text-gray-600 break-words">{m.role}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-2 text-xs text-gray-500">
                No LLMs reported
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
