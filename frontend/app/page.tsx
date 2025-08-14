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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-6">
              <div>
                <Image
                  src="/logo.png"
                  alt="MicroClear Logo"
                  width={200}
                  height={60}
                  className="h-14 w-auto"
                />
              </div>
              <div className="hidden md:flex items-center space-x-2 text-sm text-microclear-gray">
                <Shield className="w-4 h-4 text-microclear-blue" />
                <span>AI-Powered Fraud Detection</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={checkHealth}
                disabled={healthLoading}
                className="border-microclear-blue text-microclear-blue hover:bg-microclear-blue hover:text-white bg-transparent"
              >
                <Activity
                  className={`w-4 h-4 mr-2 ${
                    healthLoading ? "animate-spin" : ""
                  }`}
                />
                Test API
              </Button>
              {apiStatus === "connected" && (
                <Badge
                  variant="secondary"
                  className="bg-green-50 text-green-700 border-green-200"
                >
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Connected
                </Badge>
              )}
              {apiStatus === "error" && (
                <Badge
                  variant="destructive"
                  className="bg-red-50 text-red-700 border-red-200"
                >
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  Disconnected
                </Badge>
              )}
              {apiStatus === "checking" && (
                <Badge
                  variant="secondary"
                  className="bg-blue-50 text-blue-700 border-blue-200"
                >
                  <Activity className="w-3 h-3 mr-1 animate-spin" />
                  Checking...
                </Badge>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">
            <span className="text-[#2256AC]">Multi-Document</span>{" "}
            <span className="text-[#EC8011]">Fraud Detection Agent</span>
          </h1>
          <p className="text-lg text-microclear-gray max-w-3xl mx-auto">
            Advanced AI-powered analysis for customs fraud detection with
            intelligent pattern recognition
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1 space-y-6">
            {/* Configuration Section */}
            <div className="modern-card rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-microclear-blue rounded-lg">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Configuration
                </h3>
              </div>
              <AnalysisOptions />
            </div>

            {/* Agent Information Section */}
            <div className="modern-card rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-microclear-blue rounded-lg">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Agent Overview
                </h3>
              </div>
              <AgentInfo />
            </div>
          </div>

          <div className="lg:col-span-3 space-y-8">
            {/* Document Upload Section */}
            <div className="modern-card rounded-lg overflow-hidden">
              <div className="bg-gray-50 p-6 border-b border-gray-200">
                <div className="flex items-center space-x-4 mb-3">
                  <div className="p-2 bg-microclear-blue rounded-lg">
                    <Shield className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      Upload Documents
                    </h2>
                    <p className="text-microclear-gray text-sm">
                      Upload customs documents for fraud detection analysis
                    </p>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <FileUpload
                  onAnalysisStart={() => setIsAnalyzing(true)}
                  onAnalysisComplete={(result) => {
                    setAnalysisResult(result);
                    setIsAnalyzing(false);
                  }}
                  onAnalysisError={() => setIsAnalyzing(false)}
                  isAnalyzing={isAnalyzing}
                />
              </div>
            </div>

            {/* Analysis Results Section */}
            {analysisResult && (
              <div className="modern-card rounded-lg overflow-hidden">
                <div className="bg-gray-50 p-6 border-b border-gray-200">
                  <div className="flex items-center space-x-4 mb-3">
                    <div className="p-2 bg-microclear-blue rounded-lg">
                      <Shield className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">
                        Analysis Results
                      </h2>
                      <p className="text-microclear-gray text-sm">
                        Fraud detection analysis results and insights
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <AnalysisResults result={analysisResult} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
