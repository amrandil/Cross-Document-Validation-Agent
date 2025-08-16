"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Upload, File, X, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDocumentAnalysis } from "@/hooks/use-api";
import RealTimeAnalysis from "./real-time-analysis";
import type { AnalysisOptions } from "@/lib/api";

interface FileUploadProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: any) => void;
  onAnalysisError: () => void;
  isAnalyzing: boolean;
  activeTab?: "upload" | "thread";
  hasStarted?: boolean;
}

interface UploadedFile {
  file: File;
  id: string;
}

type PreviewData =
  | { kind: "pdf"; url: string }
  | { kind: "text"; text: string }
  | { kind: "unsupported" };

export function FileUpload({
  onAnalysisStart,
  onAnalysisComplete,
  onAnalysisError,
  isAnalyzing,
  activeTab = "upload",
  hasStarted = false,
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [filePreviews, setFilePreviews] = useState<Record<string, PreviewData>>(
    {}
  );
  const [startSignal, setStartSignal] = useState(0);
  const [internalHasStarted, setInternalHasStarted] = useState(false);
  const [hideUpload, setHideUpload] = useState(false);
  // bundleId removed per request
  const [analysisOptions, setAnalysisOptions] = useState<AnalysisOptions>({
    confidence_threshold: 0.7,
    detailed_analysis: true,
  });
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const { analyzeDocuments, error: apiError } = useDocumentAnalysis();

  const generatePreview = useCallback((id: string, file: File) => {
    if (
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")
    ) {
      const url = URL.createObjectURL(file);
      setFilePreviews((prev) => ({ ...prev, [id]: { kind: "pdf", url } }));
      return;
    }

    if (
      file.type.startsWith("text/") ||
      file.name.toLowerCase().endsWith(".txt") ||
      file.name.toLowerCase().endsWith(".csv")
    ) {
      const reader = new FileReader();
      reader.onload = () => {
        const text = typeof reader.result === "string" ? reader.result : "";
        // Limit to first ~2000 chars for preview
        setFilePreviews((prev) => ({
          ...prev,
          [id]: { kind: "text", text: text.slice(0, 2000) },
        }));
      };
      reader.onerror = () => {
        setFilePreviews((prev) => ({ ...prev, [id]: { kind: "unsupported" } }));
      };
      reader.readAsText(file);
      return;
    }

    // DOCX and others
    setFilePreviews((prev) => ({ ...prev, [id]: { kind: "unsupported" } }));
  }, []);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles = acceptedFiles.map((file) => ({
        file,
        id: Math.random().toString(36).substr(2, 9),
      }));
      setUploadedFiles((prev) => {
        const updated = [...prev, ...newFiles];
        // generate previews for the new ones
        newFiles.forEach(({ id, file }) => generatePreview(id, file));
        return updated;
      });
    },
    [generatePreview]
  );

  // Cleanup blob URLs on unmount or when files are removed
  useEffect(() => {
    return () => {
      Object.values(filePreviews).forEach((p) => {
        if (p.kind === "pdf") URL.revokeObjectURL(p.url);
      });
    };
  }, [filePreviews]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".txt"],
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/csv": [".csv"],
    },
    multiple: true,
  });

  const removeFile = (id: string) => {
    const preview = filePreviews[id];
    if (preview && preview.kind === "pdf") {
      URL.revokeObjectURL(preview.url);
    }
    setFilePreviews((prev) => {
      const clone = { ...prev };
      delete clone[id];
      return clone;
    });
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const revokeAllPreviews = () => {
    Object.values(filePreviews).forEach((p) => {
      if (p.kind === "pdf") {
        try {
          URL.revokeObjectURL(p.url);
        } catch {}
      }
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (
      Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
    );
  };

  const handleRealTimeComplete = (result: any) => {
    setAnalysisResult(result);
    onAnalysisComplete(result);
  };

  const handleRealTimeError = (error: string) => {
    onAnalysisError();
  };

  // Show upload view when activeTab is "upload" or when analysis hasn't started
  const showUploadView = activeTab === "upload" || !hasStarted;
  // Show thread view when activeTab is "thread" and analysis has started
  const showThreadView = activeTab === "thread" && hasStarted;

  return (
    <div className="h-full flex flex-col">
      {/* Upload View */}
      {showUploadView && (
        <div className="p-8 space-y-8">
          {/* Error Display */}
          {apiError && (
            <Alert variant="destructive" className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-red-700">
                {apiError}
              </AlertDescription>
            </Alert>
          )}

          {/* File Upload Area */}
          <div className="space-y-6">
            <div
              {...getRootProps()}
              className={cn(
                "border-2 border-dashed rounded-xl p-6 cursor-pointer transition-all duration-200 bg-gray-50/50 max-w-6xl mx-auto",
                isDragActive
                  ? "border-blue-400 bg-blue-50/50"
                  : "border-gray-300 hover:border-gray-400 hover:bg-gray-100/50"
              )}
            >
              <input {...getInputProps()} />
              <div className="text-center py-4">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-3" />
                <p className="text-base font-medium text-gray-700 mb-1">
                  Drop files here or click to browse
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Supports PDF, TXT, DOCX, CSV files
                </p>

                <div className="bg-gray-50 rounded-lg p-3 text-left max-w-xs mx-auto">
                  <h4 className="text-xs font-medium text-gray-700 mb-2">
                    For best results, upload:
                  </h4>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex items-center space-x-2">
                      <span className="w-1 h-1 bg-gray-400 rounded-full flex-shrink-0"></span>
                      <span>
                        <strong>Invoice</strong> - Product details, values
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-1 h-1 bg-gray-400 rounded-full flex-shrink-0"></span>
                      <span>
                        <strong>Packing List</strong> - Quantities, weights
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-1 h-1 bg-gray-400 rounded-full flex-shrink-0"></span>
                      <span>
                        <strong>Bill of Lading</strong> - Shipping info
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="w-1 h-1 bg-gray-400 rounded-full flex-shrink-0"></span>
                      <span>
                        <strong>Certificates</strong> - Origin, compliance
                      </span>
                    </div>
                  </div>
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      <strong>Tip:</strong> Upload 2-3 related documents for
                      best analysis
                    </p>
                  </div>
                </div>
              </div>

              {uploadedFiles.length > 0 && (
                <div className="mt-3">
                  <div className="flex items-center">
                    <span className="text-xs text-gray-600">
                      {uploadedFiles.length} file
                      {uploadedFiles.length > 1 ? "s" : ""} selected
                    </span>
                  </div>
                  <div className="mt-3 max-h-64 overflow-y-auto pr-1">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {uploadedFiles.map(({ file, id }) => {
                        const preview = filePreviews[id];
                        return (
                          <div
                            key={id}
                            className="p-2 bg-gray-50 rounded border"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <File className="h-5 w-5 text-gray-400" />
                                <div>
                                  <p
                                    className="font-medium text-sm truncate max-w-[12rem]"
                                    title={file.name}
                                  >
                                    {file.name}
                                  </p>
                                  <p className="text-[10px] text-gray-500">
                                    {formatFileSize(file.size)}
                                  </p>
                                </div>
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  removeFile(id);
                                }}
                                className="text-red-500 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                            <div>
                              {preview?.kind === "pdf" && (
                                <iframe
                                  src={preview.url}
                                  className="w-full h-32 rounded border bg-white"
                                  title={`preview-${id}`}
                                />
                              )}
                              {preview?.kind === "text" && (
                                <pre className="w-full max-h-32 overflow-auto text-[10px] bg-white rounded border p-1 whitespace-pre-wrap">
                                  {preview.text}
                                </pre>
                              )}
                              {preview?.kind === "unsupported" && (
                                <div className="text-xs text-gray-600">
                                  Preview not available
                                </div>
                              )}
                              {!preview && (
                                <div className="text-xs text-gray-500">
                                  Generating preview...
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Start Analysis button */}
            {!hasStarted && (
              <div className="flex justify-center pt-4">
                <Button
                  onClick={() => {
                    setInternalHasStarted(true);
                    onAnalysisStart();
                    setStartSignal((s) => s + 1);
                  }}
                  disabled={uploadedFiles.length < 2}
                  className={cn(
                    "px-8 py-2.5 font-medium",
                    uploadedFiles.length < 2
                      ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                      : "bg-gray-900 hover:bg-gray-800 text-white shadow-sm"
                  )}
                >
                  Start Analysis
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Thread View */}
      {showThreadView && (
        <div className="flex-1 min-h-0 flex flex-col">
          <RealTimeAnalysis
            files={uploadedFiles.map(({ file }) => file)}
            options={analysisOptions}
            onComplete={handleRealTimeComplete}
            onError={handleRealTimeError}
            startSignal={startSignal}
          />
        </div>
      )}
    </div>
  );
}
