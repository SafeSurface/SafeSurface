'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function Home() {
    const router = useRouter()

    useEffect(() => {
        // 重定向到 welcome 页面
        router.push('/welcome')
    }, [router])

    return null
}
