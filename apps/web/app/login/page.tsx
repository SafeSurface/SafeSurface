'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Form, Input, Button, Checkbox, Card, Typography, message, Divider } from 'antd'
import { UserOutlined, LockOutlined, SecurityScanOutlined, GithubOutlined, GoogleOutlined } from '@ant-design/icons'
import { authApi } from '@/lib/api'

const { Title, Text, Link } = Typography

type LoginForm = {
    username: string
    password: string
    remember: boolean
}

export default function LoginPage() {
    const router = useRouter()
    const [loading, setLoading] = useState(false)

    const onFinish = async (values: LoginForm) => {
        setLoading(true)
        try {
            // 调用登录 API
            await authApi.login(values.username, values.password)

            message.success('登录成功')
            router.push('/dashboard')
        } catch (error: any) {
            message.error(error.message || '登录失败，请检查用户名和密码')
        } finally {
            setLoading(false)
        }
    }

    const handleSocialLogin = (provider: string) => {
        message.info(`${provider} 登录功能开发中...`)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Logo and Title */}
                <div className="text-center mb-8 animate-fade-in">
                    <SecurityScanOutlined className="text-7xl text-purple-400 mb-4" />
                    <Title level={2} className="!text-white !mb-2">
                        欢迎回来
                    </Title>
                    <Text className="text-gray-400">
                        登录您的 SafeSurface 账户
                    </Text>
                </div>

                {/* Login Card */}
                <Card
                    className="!bg-gray-800/50 !border-gray-700 backdrop-blur-sm shadow-2xl"
                    style={{ animationDelay: '200ms' }}
                >
                    <Form
                        name="login"
                        initialValues={{ remember: true }}
                        onFinish={onFinish}
                        size="large"
                        layout="vertical"
                    >
                        <Form.Item
                            name="username"
                            rules={[
                                { required: true, message: '请输入用户名或邮箱' },
                            ]}
                        >
                            <Input
                                prefix={<UserOutlined className="text-gray-400" />}
                                placeholder="用户名或邮箱"
                                className="!bg-gray-900/50 !border-gray-600"
                            />
                        </Form.Item>

                        <Form.Item
                            name="password"
                            rules={[
                                { required: true, message: '请输入密码' },
                                { min: 6, message: '密码至少6个字符' },
                            ]}
                        >
                            <Input.Password
                                prefix={<LockOutlined className="text-gray-400" />}
                                placeholder="密码"
                                className="!bg-gray-900/50 !border-gray-600"
                            />
                        </Form.Item>

                        <Form.Item>
                            <div className="flex justify-between items-center">
                                <Form.Item name="remember" valuePropName="checked" noStyle>
                                    <Checkbox className="text-gray-300">
                                        记住我
                                    </Checkbox>
                                </Form.Item>
                                <Link href="#" className="!text-purple-400 hover:!text-purple-300">
                                    忘记密码？
                                </Link>
                            </div>
                        </Form.Item>

                        <Form.Item>
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={loading}
                                block
                                className="!bg-purple-600 hover:!bg-purple-700 !h-12 font-semibold"
                            >
                                登录
                            </Button>
                        </Form.Item>

                        <Divider className="!border-gray-600 !text-gray-400">
                            <span className="text-sm">或使用以下方式登录</span>
                        </Divider>

                        <div className="grid grid-cols-2 gap-4">
                            <Button
                                icon={<GithubOutlined />}
                                onClick={() => handleSocialLogin('GitHub')}
                                className="!bg-gray-900/50 !border-gray-600 hover:!border-purple-500"
                            >
                                GitHub
                            </Button>
                            <Button
                                icon={<GoogleOutlined />}
                                onClick={() => handleSocialLogin('Google')}
                                className="!bg-gray-900/50 !border-gray-600 hover:!border-purple-500"
                            >
                                Google
                            </Button>
                        </div>
                    </Form>

                    <div className="mt-6 text-center">
                        <Text className="text-gray-400">
                            还没有账户？{' '}
                            <Link href="#" className="!text-purple-400 hover:!text-purple-300 font-semibold">
                                立即注册
                            </Link>
                        </Text>
                    </div>
                </Card>

                {/* Footer */}
                <div className="mt-8 text-center text-gray-500 text-sm">
                    <p>© 2026 SafeSurface. All rights reserved.</p>
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
