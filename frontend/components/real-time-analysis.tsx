"use client";

import { useState, useEffect, useRef } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Activity,
  CheckCircle,
  Clock,
  FileText,
  Shield,
  Target,
  TrendingUp,
  Play,
  Pause,
  RotateCcw,
  Eye,
  EyeOff,
  Zap,
  AlertTriangle,
  Brain,
  Search,
  Calculator,
  Globe,
  Building,
  Package,
  DollarSign,
  MapPin,
  Users,
  BarChart3,
  Lightbulb,
  Filter,
  Database,
  Code,
  Terminal,
  Settings,
  Info,
  X,
  Loader2,
  MessageSquare,
  Bot,
  User,
  ChevronRight,
  ChevronDown,
  Sparkles,
  AlertCircle,
  CheckSquare,
  Square,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface StreamUpdate {
  type: string;
  timestamp: string;
  message?: string;
  execution_id?: string;
  bundle_id?: string;
  phase_number?: number;
  phase_id?: string;
  phase_name?: string;
  step_number?: number;
  step_type?: string;
  content?: string;
  tool_used?: string;
  tool_output?: string;
  total_steps?: number;
  total_phases?: number;
  tool_name?: string;
  tool_number?: number;
  total_tools?: number;
  fraud_detected?: boolean;
  risk_level?: string;
  error?: string;
}

interface RealTimeAnalysisProps {
  files: File[];
  bundleId?: string;
  options: any;
  onComplete: (result: any) => void;
  onError: (error: string) => void;
  startSignal?: number;
}

const PHASE_ICONS = {
  initial_observation: Eye,
  document_extraction: FileText,
  systematic_validation: Shield,
  pattern_detection: Brain,
  evidence_synthesis: BarChart3,
};

const STEP_ICONS = {
  OBSERVATION: Eye,
  THOUGHT: Brain,
  ACTION: Zap,
};

const TOOL_ICONS = {
  extract_data_from_document: FileText,
  validate_quantity_consistency: Calculator,
  validate_weight_consistency: Package,
  validate_entity_consistency: Building,
  validate_product_descriptions: Package,
  validate_value_consistency: DollarSign,
  validate_geographic_consistency: Globe,
  synthesize_fraud_evidence: Shield,
  detect_mathematical_anomalies: Calculator,
  detect_pattern_anomalies: Brain,
};

const PHASES = [
  {
    id: "initial_observation",
    name: "Initial Observation",
    description: "Environmental assessment",
  },
  {
    id: "document_extraction",
    name: "Document Extraction",
    description: "Data extraction",
  },
  {
    id: "systematic_validation",
    name: "Systematic Validation",
    description: "Cross-document checks",
  },
  {
    id: "pattern_detection",
    name: "Pattern Detection",
    description: "Advanced analysis",
  },
  {
    id: "evidence_synthesis",
    name: "Evidence Synthesis",
    description: "Final assessment",
  },
];

export default function RealTimeAnalysis({
  files,
  bundleId,
  options,
  onComplete,
  onError,
  startSignal,
}: RealTimeAnalysisProps) {
  const [streamUpdates, setStreamUpdates] = useState<StreamUpdate[]>([]);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [showToolDetails, setShowToolDetails] = useState(true);
  const [currentTool, setCurrentTool] = useState<string | null>(null);
  const [toolProgress, setToolProgress] = useState(0);
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [totalPhases] = useState(5);
  const [totalSteps, setTotalSteps] = useState(0);
  const [toolsUsed, setToolsUsed] = useState<string[]>([]);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [duration, setDuration] = useState(0);
  const [showDebug, setShowDebug] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);

  const streamRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startConsumedRef = useRef<number | null>(null);
  const isStartingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom when new updates arrive
  useEffect(() => {
    if (autoScroll && streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [streamUpdates, autoScroll]);

  // Update duration timer
  useEffect(() => {
    if (startTime && isStreaming) {
      intervalRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTime.getTime()) / 1000));
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [startTime, isStreaming]);

  // External trigger to start streaming
  useEffect(() => {
    if (!startSignal || startSignal <= 0) return;
    if (startConsumedRef.current === startSignal) return;
    if (isStreaming || isStartingRef.current) return;
    startConsumedRef.current = startSignal;
    void startStreaming();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startSignal]);

  const getPhaseIcon = (phaseId: string) => {
    const Icon = PHASE_ICONS[phaseId as keyof typeof PHASE_ICONS] || Target;
    return <Icon className="h-4 w-4" />;
  };

  const getStepIcon = (stepType: string) => {
    const Icon =
      STEP_ICONS[stepType as keyof typeof STEP_ICONS] || MessageSquare;
    return <Icon className="h-4 w-4" />;
  };

  const getToolIcon = (toolName: string) => {
    const Icon = TOOL_ICONS[toolName as keyof typeof TOOL_ICONS] || Settings;
    return <Icon className="h-4 w-4" />;
  };

  const getPhaseProgress = () => {
    return ((currentPhase - 1) / totalPhases) * 100;
  };

  const getPhaseColor = (phaseNumber: number) => {
    if (phaseNumber < currentPhase) return "border-green-500 bg-green-50";
    if (phaseNumber === currentPhase) return "border-blue-500 bg-blue-50";
    return "border-gray-200 bg-gray-50";
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const startStreaming = async () => {
    if (files.length === 0) {
      setError("No files selected");
      return;
    }

    if (abortControllerRef.current) {
      try {
        abortControllerRef.current.abort();
      } catch {}
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    isStartingRef.current = true;
    setIsStreaming(true);
    setError(null);
    setStreamUpdates([]);
    setCurrentPhase(1);
    setTotalSteps(0);
    setToolsUsed([]);
    setStartTime(new Date());
    setDuration(0);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    formData.append("options", JSON.stringify(options));

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/analyze/stream",
        {
          method: "POST",
          body: formData,
          signal: controller.signal,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        let boundary = buffer.indexOf("\n\n");
        while (boundary !== -1) {
          const rawEvent = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);

          // Parse SSE event lines (ignore comments starting with ':')
          const lines = rawEvent.split("\n").filter((l) => !l.startsWith(":"));
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data.trim() === "") continue;
              try {
                const update: StreamUpdate = JSON.parse(data);
                handleStreamUpdate(update);
              } catch (e) {
                console.error("Error parsing stream update:", e, line);
              }
            }
          }

          boundary = buffer.indexOf("\n\n");
        }
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        return;
      }
      console.error("Streaming error:", err);
      setError(err instanceof Error ? err.message : "Streaming failed");
      setIsStreaming(false);
    } finally {
      isStartingRef.current = false;
    }
  };

  const handleStreamUpdate = (update: StreamUpdate) => {
    console.log("Received stream update:", update);

    setStreamUpdates((prev) => [...prev, update]);

    switch (update.type) {
      case "analysis_started":
        setExecutionId(update.execution_id || null);
        break;

      case "phase_started":
        if (update.phase_number) {
          setCurrentPhase(update.phase_number);
        }
        break;

      case "step_completed":
        if (update.total_steps) {
          setTotalSteps(update.total_steps);
        }
        if (update.tool_used && !toolsUsed.includes(update.tool_used)) {
          setToolsUsed((prev) => [...prev, update.tool_used!]);
        }
        break;

      case "tool_progress":
        setCurrentTool(update.tool_name || null);
        if (update.tool_number && update.total_tools) {
          setToolProgress((update.tool_number / update.total_tools) * 100);
        }
        break;

      case "analysis_completed":
        setIsStreaming(false);
        if (update.fraud_detected !== undefined) {
          onComplete({
            fraud_detected: update.fraud_detected,
            risk_level: update.risk_level,
            execution_id: update.execution_id,
          });
        }
        break;

      case "analysis_error":
        setIsStreaming(false);
        setError(update.error || "Analysis failed");
        onError(update.error || "Analysis failed");
        break;

      case "keepalive":
        // Just keep the connection alive
        break;
    }
  };

  const pauseStreaming = () => {
    setIsPaused(!isPaused);
  };

  const resetAnalysis = () => {
    setIsStreaming(false);
    setIsPaused(false);
    setStreamUpdates([]);
    setCurrentPhase(0);
    setTotalSteps(0);
    setToolsUsed([]);
    setCurrentTool(null);
    setToolProgress(0);
    setExecutionId(null);
    setError(null);
    setStartTime(null);
    setDuration(0);
  };

  const getStepTypeColor = (stepType: string) => {
    switch (stepType) {
      case "OBSERVATION":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "THOUGHT":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "ACTION":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStepTypeIcon = (stepType: string) => {
    switch (stepType) {
      case "OBSERVATION":
        return <Eye className="h-4 w-4" />;
      case "THOUGHT":
        return <Brain className="h-4 w-4" />;
      case "ACTION":
        return <Zap className="h-4 w-4" />;
      default:
        return <MessageSquare className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Real-time Reasoning Thread */}
      <Card>
        {/*<CardHeader className="py-3">
          <CardTitle className="flex items-center space-x-2 text-base">
            <MessageSquare className="h-4 w-4" />
            <span>Agent Reasoning</span>
          </CardTitle>
        </CardHeader>*/}
        <CardContent>
          <ScrollArea
            ref={streamRef}
            className="h-[600px] w-full border rounded-lg p-4"
          >
            <div className="space-y-4">
              {/* Welcome Message */}
              {streamUpdates.length === 0 && !isStreaming && (
                <div className="text-center py-8 text-gray-500">
                  <Bot className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Ready to Start Analysis</p>
                  <p className="text-sm">
                    Click "Start Analysis" to begin the fraud detection process
                  </p>
                </div>
              )}

              {/* Loading Message */}
              {streamUpdates.length === 0 && isStreaming && (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  <p>Initializing agent and connecting to analysis stream...</p>
                </div>
              )}

              {/* Stream Updates */}
              {streamUpdates.map((update, index) => {
                // Handle different update types
                if (update.type === "step_completed" && update.step_type) {
                  return (
                    <div key={index} className="flex space-x-3">
                      {/* Agent Avatar */}
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>

                      {/* Message Content */}
                      <div className="flex-1 min-w-0">
                        <div className="bg-white border rounded-lg p-4 shadow-sm">
                          {/* Header */}
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Badge
                                variant="outline"
                                className={cn(
                                  "text-xs",
                                  getStepTypeColor(update.step_type)
                                )}
                              >
                                {getStepTypeIcon(update.step_type)}
                                <span className="ml-1">{update.step_type}</span>
                              </Badge>
                              {update.step_number && (
                                <Badge variant="secondary" className="text-xs">
                                  Step {update.step_number}
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-gray-500 flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {new Date(update.timestamp).toLocaleTimeString()}
                            </div>
                          </div>

                          {/* Content */}
                          <div className="prose prose-sm max-w-none">
                            <p className="text-gray-800 whitespace-pre-wrap">
                              {update.content}
                            </p>
                          </div>

                          {/* Tool Information */}
                          {update.tool_used && (
                            <div className="mt-3 pt-3 border-t border-gray-100">
                              <div className="flex items-center space-x-2 mb-2">
                                {getToolIcon(update.tool_used)}
                                <span className="text-sm font-medium text-gray-700">
                                  Tool: {update.tool_used.replace(/_/g, " ")}
                                </span>
                              </div>

                              {showToolDetails && update.tool_output && (
                                <div className="bg-gray-50 p-3 rounded border">
                                  <div className="text-xs font-medium text-gray-600 mb-1">
                                    Tool Output:
                                  </div>
                                  <pre className="text-xs bg-white p-2 rounded border overflow-x-auto max-h-32">
                                    {update.tool_output}
                                  </pre>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }

                // Handle phase updates
                if (update.type === "phase_started") {
                  return (
                    <div key={index} className="flex space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                          <Target className="h-4 w-4 text-purple-600" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                          <div className="flex items-center space-x-2">
                            {getPhaseIcon(update.phase_id || "")}
                            <span className="font-medium text-purple-800">
                              Phase {update.phase_number}: {update.phase_name}
                            </span>
                          </div>
                          {update.message && (
                            <p className="text-sm text-purple-700 mt-1">
                              {update.message}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }

                // Handle tool progress
                if (update.type === "tool_progress") {
                  return (
                    <div key={index} className="flex space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                          <Settings className="h-4 w-4 text-green-600" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="flex items-center space-x-2">
                            {getToolIcon(update.tool_name || "")}
                            <span className="font-medium text-green-800">
                              Running: {update.tool_name?.replace(/_/g, " ")}
                            </span>
                          </div>
                          {update.message && (
                            <p className="text-sm text-green-700 mt-1">
                              {update.message}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }

                // Handle analysis completion
                if (update.type === "analysis_completed") {
                  return (
                    <div key={index} className="flex space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            <span className="font-medium text-green-800">
                              Analysis Completed
                            </span>
                          </div>
                          <p className="text-sm text-green-700">
                            Fraud detection analysis has been completed
                            successfully.
                          </p>
                          {update.fraud_detected !== undefined && (
                            <div className="mt-2">
                              <Badge
                                variant={
                                  update.fraud_detected
                                    ? "destructive"
                                    : "default"
                                }
                                className="mr-2"
                              >
                                {update.fraud_detected
                                  ? "Fraud Detected"
                                  : "No Fraud Detected"}
                              </Badge>
                              {update.risk_level && (
                                <Badge variant="outline">
                                  Risk: {update.risk_level}
                                </Badge>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }

                // Handle errors
                if (update.type === "analysis_error") {
                  return (
                    <div key={index} className="flex space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-2">
                            <AlertTriangle className="h-5 w-5 text-red-600" />
                            <span className="font-medium text-red-800">
                              Analysis Error
                            </span>
                          </div>
                          <p className="text-sm text-red-700">
                            {update.error ||
                              "An error occurred during analysis"}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                }

                // Default case for other update types
                return (
                  <div key={index} className="flex space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                        <Info className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                        <div className="text-sm text-gray-700">
                          {update.message || JSON.stringify(update)}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Debug Panel */}
      {showDebug && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Terminal className="h-5 w-5" />
              <span>Debug Information</span>
            </CardTitle>
            <CardDescription>
              Raw stream updates and system information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">System Status</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Is Streaming:</span>{" "}
                    {isStreaming ? "Yes" : "No"}
                  </div>
                  <div>
                    <span className="font-medium">Current Phase:</span>{" "}
                    {currentPhase}
                  </div>
                  <div>
                    <span className="font-medium">Total Updates:</span>{" "}
                    {streamUpdates.length}
                  </div>
                  <div>
                    <span className="font-medium">Step Updates:</span>{" "}
                    {
                      streamUpdates.filter((u) => u.type === "step_completed")
                        .length
                    }
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Recent Updates (Last 10)</h4>
                <div className="max-h-64 overflow-y-auto bg-gray-50 p-3 rounded border">
                  {streamUpdates.slice(-10).map((update, index) => (
                    <div
                      key={index}
                      className="text-xs mb-2 p-2 bg-white rounded border"
                    >
                      <div className="font-medium text-blue-600">
                        {update.type}
                      </div>
                      <div className="text-gray-600">{update.timestamp}</div>
                      {update.message && (
                        <div className="text-gray-800">{update.message}</div>
                      )}
                      {update.step_type && (
                        <div className="text-gray-800">
                          Step: {update.step_type}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
