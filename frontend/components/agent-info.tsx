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
      {/* Expandable Header */}
      <div className="flex items-center justify-between">
        <Button
          onClick={() => setIsExpanded(!isExpanded)}
          variant="ghost"
          size="sm"
          className="h-6 px-2 hover:bg-gray-100"
        >
          {isExpanded ? (
            <ChevronDown className="h-3 w-3 mr-1" />
          ) : (
            <ChevronRight className="h-3 w-3 mr-1" />
          )}
          <span className="text-xs text-gray-700">Agent Overview</span>
        </Button>
        <div className="flex items-center space-x-2">
          <Button
            onClick={fetchAgentInfo}
            disabled={loading}
            variant="outline"
            size="sm"
            className="h-6 w-6 p-0"
          >
            <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          </Button>
          {agentInfo && (
            <Badge className="bg-green-100 text-green-800 border-green-200 text-xs h-5">
              Active
            </Badge>
          )}
        </div>
      </div>

      {loading && (
        <Card className="text-xs">
          <CardContent className="flex items-center justify-center py-3">
            <RefreshCw className="h-4 w-4 animate-spin text-microclear-blue mr-2" />
            <span>Loading...</span>
          </CardContent>
        </Card>
      )}

      {agentInfo && isExpanded && (
        <div className="space-y-3">
          {/* Compact Agent Overview */}
          <Card className="text-xs">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm">
                <Bot className="h-4 w-4 mr-1" />
                Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <div className="text-center p-2 bg-blue-50 rounded border border-blue-200">
                  <Tool className="h-4 w-4 text-microclear-blue mx-auto mb-1" />
                  <p className="text-xs text-gray-600">Tools</p>
                  <p className="font-semibold text-xs">
                    {agentInfo.tools_count || agentInfo.tools?.length || 0}
                  </p>
                </div>
                <div className="text-center p-2 bg-green-50 rounded border border-green-200">
                  <FileText className="h-4 w-4 text-green-600 mx-auto mb-1" />
                  <p className="text-xs text-gray-600">Docs</p>
                  <p className="font-semibold text-xs">
                    {agentInfo.supported_document_types?.length || "Multiple"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compact Document Types */}
          <Card className="text-xs">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm">
                <FileText className="h-4 w-4 mr-1" />
                Document Types
              </CardTitle>
            </CardHeader>
            <CardContent>
              {agentInfo.supported_document_types &&
              agentInfo.supported_document_types.length > 0 ? (
                <div className="space-y-1">
                  {agentInfo.supported_document_types
                    .slice(0, 3)
                    .map((type: string) => (
                      <div
                        key={type}
                        className="flex items-center p-1 bg-gray-50 rounded text-xs"
                      >
                        <FileText className="h-3 w-3 text-microclear-blue mr-1" />
                        <span className="truncate">
                          {type
                            .replace("_", " ")
                            .replace(/\b\w/g, (l: string) => l.toUpperCase())}
                        </span>
                      </div>
                    ))}
                  {agentInfo.supported_document_types.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{agentInfo.supported_document_types.length - 3} more
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-2">
                  <FileText className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">
                    Multiple formats supported
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Compact Fraud Types */}
          <Card className="text-xs">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm">
                <Shield className="h-4 w-4 mr-1" />
                Fraud Detection
              </CardTitle>
            </CardHeader>
            <CardContent>
              {agentInfo.fraud_types_detected &&
              agentInfo.fraud_types_detected.length > 0 ? (
                <div className="space-y-1">
                  {agentInfo.fraud_types_detected
                    .slice(0, 3)
                    .map((type: string) => (
                      <div
                        key={type}
                        className="flex items-center p-1 bg-red-50 rounded border border-red-200 text-xs"
                      >
                        <AlertTriangle className="h-3 w-3 text-red-600 mr-1" />
                        <span className="truncate text-red-800">
                          {type
                            .replace("_", " ")
                            .replace(/\b\w/g, (l: string) => l.toUpperCase())}
                        </span>
                      </div>
                    ))}
                  {agentInfo.fraud_types_detected.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{agentInfo.fraud_types_detected.length - 3} more
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-2">
                  <Shield className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">
                    Multiple patterns detected
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Compact Tools */}
          <Card className="text-xs">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm">
                <Tool className="h-4 w-4 mr-1" />
                Analysis Tools
              </CardTitle>
            </CardHeader>
            <CardContent>
              {agentInfo.tools && agentInfo.tools.length > 0 ? (
                <div className="space-y-1">
                  {agentInfo.tools
                    .slice(0, 4)
                    .map((tool: string, index: number) => (
                      <div
                        key={index}
                        className="flex items-center p-1 bg-gray-50 rounded text-xs"
                      >
                        {getCapabilityIcon(tool)}
                        <span className="ml-1 truncate">{tool}</span>
                      </div>
                    ))}
                  {agentInfo.tools.length > 4 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{agentInfo.tools.length - 4} more tools
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-2">
                  <Tool className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">
                    Multiple tools available
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Compact Status */}
          <Card className="text-xs">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 mr-1" />
                Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center p-2 bg-green-50 rounded border border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                <div>
                  <p className="font-medium text-green-800 text-xs">Online</p>
                  <p className="text-xs text-green-600">Ready for analysis</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
