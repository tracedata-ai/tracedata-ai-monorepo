import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReactFlowProvider, type Node } from "@xyflow/react";

import { AgentNode } from "./AgentNode";
import type { AgentNodeData } from "./flow-data";

describe("AgentNode", () => {
  it("renders queued status with worker health badge", () => {
    const node: Node<AgentNodeData> = {
      id: "safety",
      position: { x: 0, y: 0 },
      data: {
        label: "Safety Agent",
        subtitle: "Emergency + Alert",
        status: "queued",
        workerHealth: "degraded",
        type: "agent",
      },
      type: "agentNode",
    };

    render(
      <ReactFlowProvider>
        <AgentNode
          id={node.id}
          data={node.data}
          type="agentNode"
          selected={false}
          dragging={false}
          zIndex={1}
          selectable
          deletable
          draggable
          isConnectable={false}
          positionAbsoluteX={0}
          positionAbsoluteY={0}
        />
      </ReactFlowProvider>
    );
    expect(screen.getByText(/queued/i)).toBeInTheDocument();
    expect(screen.getByText(/degraded/i)).toBeInTheDocument();
    expect(screen.getByText(/Safety Agent/i)).toBeInTheDocument();
  });
});
