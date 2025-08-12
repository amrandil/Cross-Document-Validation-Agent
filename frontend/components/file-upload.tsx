"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Upload,
  File,
  X,
  ChevronDown,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useDocumentAnalysis } from "@/hooks/use-api";
import type { AnalysisOptions } from "@/lib/api";

interface FileUploadProps {
  onAnalysisStart: () => void;
  onAnalysisComplete: (result: any) => void;
  onAnalysisError: () => void;
  isAnalyzing: boolean;
}

interface UploadedFile {
  file: File;
  id: string;
}

export function FileUpload({
  onAnalysisStart,
  onAnalysisComplete,
  onAnalysisError,
  isAnalyzing,
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [bundleId, setBundleId] = useState("");
  const [analysisOptions, setAnalysisOptions] = useState<AnalysisOptions>({
    confidence_threshold: 0.7,
    detailed_analysis: true,
  });
  const [showFileDetails, setShowFileDetails] = useState(false);

  const { analyzeDocuments, error: apiError } = useDocumentAnalysis();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
    }));
    setUploadedFiles((prev) => [...prev, ...newFiles]);
  }, []);

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
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
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

  const handleAnalyzeDocuments = async () => {
    if (uploadedFiles.length === 0) {
      return;
    }

    onAnalysisStart();

    try {
      const result = await analyzeDocuments({
        files: uploadedFiles.map(({ file }) => file),
        bundle_id: bundleId.trim() || undefined,
        options: analysisOptions,
      });
      onAnalysisComplete(result);
    } catch (error) {
      onAnalysisError();
    }
  };

  return (
    <div className="space-y-6">
      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-microclear-blue bg-blue-50"
            : "border-gray-300 hover:border-microclear-blue hover:bg-gray-50"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-microclear-blue font-medium">
            Drop the files here...
          </p>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              Choose document files or drag and drop
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, TXT, DOCX, CSV files for customs document analysis
            </p>
          </div>
        )}
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="font-medium">
                  {uploadedFiles.length} files uploaded
                </span>
              </div>
              <Collapsible
                open={showFileDetails}
                onOpenChange={setShowFileDetails}
              >
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" size="sm">
                    File Details
                    <ChevronDown
                      className={cn(
                        "h-4 w-4 ml-2 transition-transform",
                        showFileDetails && "rotate-180"
                      )}
                    />
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-4">
                  <div className="space-y-2">
                    {uploadedFiles.map(({ file, id }) => (
                      <div
                        key={id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <File className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="font-medium text-sm">{file.name}</p>
                            <p className="text-xs text-gray-500">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bundle ID Input */}
      <div className="space-y-2">
        <Label htmlFor="bundle-id">Bundle ID (optional)</Label>
        <Input
          id="bundle-id"
          placeholder="Leave empty to auto-generate"
          value={bundleId}
          onChange={(e) => setBundleId(e.target.value)}
          className="max-w-md"
        />
        <p className="text-sm text-gray-500">
          Unique identifier for this document bundle
        </p>
      </div>

      {/* Error Display */}
      {apiError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{apiError}</AlertDescription>
        </Alert>
      )}

      {/* Analysis Button */}
      <div className="flex justify-center">
        <Button
          onClick={handleAnalyzeDocuments}
          disabled={uploadedFiles.length === 0 || isAnalyzing}
          className="bg-microclear-blue hover:bg-microclear-blue-light text-white px-8 py-2"
          size="lg"
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Analyzing Documents...
            </>
          ) : (
            "Analyze Documents"
          )}
        </Button>
      </div>

      {/* Analysis Progress */}
      {isAnalyzing && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  Analyzing documents for fraud indicators...
                </span>
                <Badge variant="secondary">Processing</Badge>
              </div>
              <Progress value={undefined} className="w-full" />
              <p className="text-xs text-gray-500 text-center">
                This may take up to 10 minutes depending on document complexity
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
