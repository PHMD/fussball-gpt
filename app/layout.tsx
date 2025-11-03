import type { Metadata } from 'next'
import './globals.css'
import { FeedLayoutWrapper } from '@/components/feed/feed-layout-wrapper'
import { ThemeProvider } from '@/components/theme-provider'

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
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <FeedLayoutWrapper>{children}</FeedLayoutWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}
