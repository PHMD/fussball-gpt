import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Fußball GPT',
  description: 'German football intelligence assistant powered by AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}
