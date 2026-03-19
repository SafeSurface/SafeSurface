# SafeSurface 进阶架构设计 (Advanced Architecture)

## 1. 架构核心思想

SafeSurface 采用 **分层规划与反思执行架构（Hierarchical Plan-and-Solve with Reflection）**，结合 LangGraph 的高级特性（如 Sub-graphs、Checkpoints 回溯记忆机制以及 Human-in-the-loop 人类闭环），旨在模拟真实专业渗透测试团队的作业流。

以下是四个维度的核心突破：
1. **战略与战术分离（Hierarchical Sub-graphs 分层子图）**：分为主脑（Master Planner）和专业团队（各个 Sub-graph）。
2. **Actor-Critic 反思与验证机制**：在 Payload 投递及漏洞利用等子图中引入 Critic 验证机制，对失败结果通过局部循环进行自我修正。
3. **动态攻击面状态追踪（Global Attack Tree State）**：全局统一的共享黑板（Blackboard 模式），记录动态攻击树、资产库、隐患等信息。
4. **Human-in-the-Loop (HITL) 与检查点**：在执行高风险工具前，中断执行并进行人工确认。

## 2. 核心架构图

``mermaid
graph TD
    %% 用户与接入层
    User((Penetration Tester)) <--> |Human-in-the-loop / Auth| API[API Gateway]
    
    %% 全局状态与记忆 (LangGraph Memory & Checkpoints)
    subgraph "Core Memory & State (LangGraph Checkpoints)"
        GlobalState[Global State: <br/>Attack Tree, Assets, Creds, Vulns]
    end

    API <--> MasterPlanner
    
    %% 第一层：战略规划层 (The Brain)
    subgraph "Layer 1: Strategy & Planning"
        MasterPlanner[Master Planner Agent组长]
        AttackTreeManager[攻击树状态维护]
        MasterPlanner <--> AttackTreeManager
        MasterPlanner -.-> |Read/Write| GlobalState
    end

    %% 第二层：战术执行层 (Sub-graphs 嵌套子图)
    MasterPlanner --> |Delegate Task| ReconTeam
    MasterPlanner --> |Delegate Task| VulnResearchTeam
    MasterPlanner --> |Delegate Task| ExploitTeam
    
    subgraph "Layer 2: Tactical Execution (LangGraph Sub-graphs)"
        
        %% 侦察子团队
        subgraph ReconTeam [Recon Sub-graph]
            OSINT_Agent[OSINT Agent]
            Scanner_Agent[Scanner Agent]
        end
        
        %% 漏洞研究子团队 (重度依赖 RAG)
        subgraph VulnResearchTeam [Vuln Research Sub-graph]
            VulnAnalyzer[Vulnerability Analyzer]
            PayloadCrafter[Payload Crafter]
            VulnAnalyzer <--> |RAG| VectorDB[(CVE / ExploitDB / TTPs)]
            PayloadCrafter <--> |RAG| VectorDB
        end
        
        %% 漏洞利用与绕过子团队 (Actor-Critic 循环)
        subgraph ExploitTeam [Exploit & Bypass Sub-graph]
            Executor[Execution Agent]
            Validator[Critic / Validator Agent]
            Executor --> |Execute Payload| Validator
            Validator --> |Analyze Logs/Errors<br/>Provide Feedback| Executor
        end
        
    end

    %% 第三层：物理隔离执行层 (MCP)
    ReconTeam -.-> |Tool Calls via MCP| MCP_Client
    ExploitTeam -.-> |Tool Calls via MCP| MCP_Client
    
    subgraph "Layer 3: Protocol & Physical Execution Layer"
        MCP_Client[MCP Client Broker]
        MCP_Client <--> Nmap[(Nmap MCP Server)]
        MCP_Client <--> MSF[(Metasploit MCP Server)]
        MCP_Client <--> Sandbox[(Docker Sandbox Exec)]
    end
``

## 3. 技术栈
- **核心框架**: LangChain, LangGraph
- **底层依赖**: uv (Python Package Manager), Pydantic (State definition)
- **协议层**: MCP (Model Context Protocol) 隔离重度系统依赖工具
- **知识库体系**: RAG (向量检索，用于查询渗透测试库、CVE百科和内部 Runbooks)
