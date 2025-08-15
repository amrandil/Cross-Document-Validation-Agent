"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { RefreshCw, Bot, AlertCircle } from "lucide-react";
import { useAgentInfo } from "@/hooks/use-api";

export function AgentInfo() {
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
        <div className="text-xs text-gray-600 flex items-center">
          <RefreshCw className="h-3 w-3 animate-spin text-microclear-blue mr-2" />
          Loading...
        </div>
      )}

      {agentInfo && (
        <div className="space-y-2">
          {agentInfo.agent_type && (
            <div className="flex items-start">
              <Bot className="h-3 w-3 text-microclear-blue mt-0.5 mr-2" />
              <div className="min-w-0">
                <div className="font-medium break-words">
                  {agentInfo.agent_type}
                </div>
              </div>
            </div>
          )}

          {agentInfo.tools && agentInfo.tools.length > 0 && (
            <div>
              <div className="text-[11px] text-gray-600 mb-1">Tools</div>
              <ul className="list-disc ml-5 space-y-0.5">
                {agentInfo.tools.slice(0, 6).map((tool, idx) => (
                  <li
                    key={idx}
                    className="text-[11px] text-gray-700 break-words"
                  >
                    {tool}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
