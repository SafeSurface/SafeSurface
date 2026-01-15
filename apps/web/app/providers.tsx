'use client'

import { ConfigProvider, theme } from 'antd'
import { AntdRegistry } from '@ant-design/nextjs-registry'

export default function Providers({ children }: { children: React.ReactNode }) {
    return (
        <AntdRegistry>
            <ConfigProvider
                theme={{
                    algorithm: theme.darkAlgorithm,
                    token: {
                        colorPrimary: '#7c4dff',
                        colorBgBase: '#0a0a0a',
                        borderRadius: 8,
                    },
                }}
            >
                {children}
            </ConfigProvider>
        </AntdRegistry>
    )
}
