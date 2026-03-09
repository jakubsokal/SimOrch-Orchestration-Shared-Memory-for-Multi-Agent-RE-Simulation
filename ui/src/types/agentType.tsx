export const AgentType = {
    REQUIREMENTS_ENGINEER: 1,
    STAKEHOLDER: 2,
} as const;

export type AgentType = typeof AgentType[keyof typeof AgentType];

export const AgentTypeLabels: Record<AgentType, string> = {
    [AgentType.REQUIREMENTS_ENGINEER]: "Requirements Engineer",
    [AgentType.STAKEHOLDER]: "Stakeholder",
};