import { createContext, useContext, useState } from 'react'

const StudyChatContext = createContext({ studyContext: null, setStudyContext: () => {} })

export function StudyChatProvider({ children }) {
  const [studyContext, setStudyContext] = useState(null)
  return (
    <StudyChatContext.Provider value={{ studyContext, setStudyContext }}>
      {children}
    </StudyChatContext.Provider>
  )
}

export function useStudyChat() {
  return useContext(StudyChatContext)
}
