"use client";

import { useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileUpload } from "@/components/file-upload";
import { AnalysisOptions } from "@/components/analysis-options";
import { AnalysisResults } from "@/components/analysis-results";
import { AgentInfo } from "@/components/agent-info";
import { CheckCircle, AlertTriangle, Activity, Shield } from "lucide-react";
import { useHealthCheck } from "@/hooks/use-api";

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [activeTab, setActiveTab] = useState<"upload" | "thread">("upload");

  const {
    data: healthData,
    loading: healthLoading,
    error: healthError,
    checkHealth,
  } = useHealthCheck();

  const getApiStatus = () => {
    if (healthLoading) return "checking";
    if (healthError) return "error";
    if (healthData) return "connected";
    return "unknown";
  };

  const apiStatus = getApiStatus();

  return (
    <div className="min-h-screen bg-white">
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/60 sticky top-0 z-50">
        <div className="mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-6">
              <div>
                <Image
                  src="/logo.png"
                  alt="MicroClear Logo"
                  width={180}
                  height={50}
                  className="h-10 w-auto"
                />
              </div>
              <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
                <Shield className="w-4 h-4 text-gray-500" />
                <span>AI-Powered Cross-Document Validation Agent</span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={checkHealth}
                disabled={healthLoading}
                className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-transparent h-8 px-3 text-xs"
              >
                <Activity
                  className={`w-3 h-3 mr-1.5 ${
                    healthLoading ? "animate-spin" : ""
                  }`}
                />
                Test API
              </Button>
              {apiStatus === "connected" && (
                <Badge
                  variant="secondary"
                  className="bg-green-50 text-green-600 border-green-200 text-xs px-2 py-0.5"
                >
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Connected
                </Badge>
              )}
              {apiStatus === "error" && (
                <Badge
                  variant="destructive"
                  className="bg-red-50 text-red-600 border-red-200 text-xs px-2 py-0.5"
                >
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  Disconnected
                </Badge>
              )}
              {apiStatus === "checking" && (
                <Badge
                  variant="secondary"
                  className="bg-blue-50 text-blue-600 border-blue-200 text-xs px-2 py-0.5"
                >
                  <Activity className="w-3 h-3 mr-1 animate-spin" />
                  Checking...
                </Badge>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="h-[calc(100vh-64px)] flex">
        {/* Sidebar */}
        <aside className="w-64 shrink-0 border-r border-gray-200/60 bg-gray-50/30">
          <div className="h-full overflow-y-auto px-6 py-8 space-y-12">
            <div>
              <h3 className="text-xs font-medium text-gray-900 mb-4 uppercase tracking-wide">
                Confidence Threshold
              </h3>
              <AnalysisOptions />
            </div>

            <div>
              <h3 className="text-xs font-medium text-gray-900 mb-4 uppercase tracking-wide">
                Agent Information
              </h3>
              <AgentInfo />
            </div>
          </div>
        </aside>

        {/* Right Pane */}
        <section className="flex-1 flex flex-col min-w-0 bg-white">
          <div className="px-8 py-6 border-b border-gray-200/60 bg-white/80 backdrop-blur-sm">
            {hasStarted ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-8">
                  <button
                    onClick={() => setActiveTab("upload")}
                    className={`pb-3 px-1 text-sm font-medium border-b-2 transition-all duration-200 ${
                      activeTab === "upload"
                        ? "border-gray-900 text-gray-900"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Upload Documents
                  </button>
                  <button
                    onClick={() => setActiveTab("thread")}
                    className={`pb-3 px-1 text-sm font-medium border-b-2 transition-all duration-200 ${
                      activeTab === "thread"
                        ? "border-gray-900 text-gray-900"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Agent Thread
                  </button>
                </div>
                <div>
                  <h1 className="text-xl font-medium text-gray-900 mb-1">
                    {activeTab === "upload"
                      ? "Upload Documents"
                      : "Agent Analysis"}
                  </h1>
                  <p className="text-sm text-gray-600">
                    {activeTab === "upload"
                      ? "Upload additional documents or manage existing files"
                      : "Live reasoning stream from the agent"}
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <h1 className="text-xl font-medium text-gray-900 mb-1">
                  Upload Documents
                </h1>
                <p className="text-sm text-gray-600">
                  Upload your documents, then start analysis. Minimum 2 files
                  recommended.
                </p>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-hidden">
            <div className="h-full">
              <FileUpload
                onAnalysisStart={() => {
                  setIsAnalyzing(true);
                  setHasStarted(true);
                  setActiveTab("thread");
                }}
                onAnalysisComplete={(result) => {
                  setAnalysisResult(result);
                  setIsAnalyzing(false);
                }}
                onAnalysisError={() => setIsAnalyzing(false)}
                isAnalyzing={isAnalyzing}
                activeTab={activeTab}
                hasStarted={hasStarted}
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
