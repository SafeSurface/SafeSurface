'use client'

import { useRouter } from 'next/navigation'
import { Button, Card, Typography } from 'antd'
import { SecurityScanOutlined, RocketOutlined, SafetyOutlined, ThunderboltOutlined } from '@ant-design/icons'

const { Title, Paragraph } = Typography

export default function WelcomePage() {
    const router = useRouter()

    const features = [
        {
            icon: <SecurityScanOutlined className="text-5xl text-purple-500" />,
            title: 'AI智能分析',
            description: '基于大模型的智能漏洞分析和攻击路径规划',
        },
        {
            icon: <ThunderboltOutlined className="text-5xl text-blue-500" />,
            title: '自动化测试',
            description: '7个Agent协同工作，自动化渗透测试流程',
        },
        {
            icon: <SafetyOutlined className="text-5xl text-green-500" />,
            title: '全程可追溯',
            description: '完整的审计日志和证据链，确保合规性',
        },
        {
            icon: <RocketOutlined className="text-5xl text-orange-500" />,
            title: '持续学习',
            description: 'Agent记忆系统持续优化测试策略',
        },
    ]

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-8">
            <div className="max-w-6xl w-full">
                {/* Hero Section */}
                <div className="text-center mb-16 animate-fade-in">
                    <div className="mb-6">
                        <SecurityScanOutlined className="text-8xl text-purple-400 animate-pulse" />
                    </div>
                    <Title level={1} className="!text-white !mb-4 !text-6xl font-bold">
                        SafeSurface
                    </Title>
                    <Title level={2} className="!text-purple-300 !mb-6 !text-2xl font-light">
                        AI Agent 驱动的智能渗透测试平台
                    </Title>
                    <Paragraph className="text-gray-300 text-lg max-w-2xl mx-auto mb-8">
                        基于先进的大语言模型和多Agent协同技术，为您提供全自动化、智能化的安全测试解决方案
                    </Paragraph>

                    <div className="flex gap-4 justify-center">
                        <Button
                            type="primary"
                            size="large"
                            icon={<RocketOutlined />}
                            onClick={() => router.push('/login')}
                            className="!bg-purple-600 hover:!bg-purple-700 !h-12 !px-8 !text-lg font-semibold"
                        >
                            开始使用
                        </Button>
                        <Button
                            size="large"
                            onClick={() => window.open('https://github.com', '_blank')}
                            className="!h-12 !px-8 !text-lg"
                        >
                            了解更多
                        </Button>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, index) => (
                        <Card
                            key={index}
                            hoverable
                            className="!bg-gray-800/50 !border-gray-700 backdrop-blur-sm transition-all duration-300 hover:!bg-gray-800/70 hover:scale-105"
                            style={{ animationDelay: `${index * 100}ms` }}
                        >
                            <div className="text-center">
                                <div className="mb-4">{feature.icon}</div>
                                <Title level={4} className="!text-white !mb-2">
                                    {feature.title}
                                </Title>
                                <Paragraph className="!text-gray-400 !mb-0">
                                    {feature.description}
                                </Paragraph>
                            </div>
                        </Card>
                    ))}
                </div>

                {/* Stats Section */}
                <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                    <div className="p-6 bg-gray-800/30 rounded-lg backdrop-blur-sm border border-gray-700">
                        <Title level={2} className="!text-purple-400 !mb-2">
                            7+
                        </Title>
                        <Paragraph className="!text-gray-300 !mb-0">
                            智能Agent
                        </Paragraph>
                    </div>
                    <div className="p-6 bg-gray-800/30 rounded-lg backdrop-blur-sm border border-gray-700">
                        <Title level={2} className="!text-blue-400 !mb-2">
                            100%
                        </Title>
                        <Paragraph className="!text-gray-300 !mb-0">
                            自动化覆盖
                        </Paragraph>
                    </div>
                    <div className="p-6 bg-gray-800/30 rounded-lg backdrop-blur-sm border border-gray-700">
                        <Title level={2} className="!text-green-400 !mb-2">
                            24/7
                        </Title>
                        <Paragraph className="!text-gray-300 !mb-0">
                            持续监控
                        </Paragraph>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-16 text-center text-gray-500 text-sm">
                    <p>© 2026 SafeSurface. AI-driven Security Testing Platform.</p>
                </div>
            </div>

            <style jsx global>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
      `}</style>
        </div>
    )
}
