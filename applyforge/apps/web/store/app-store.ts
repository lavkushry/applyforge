import { create } from 'zustand'
export const useAppStore = create<{viewMode:'table'|'cards';setViewMode:(mode:'table'|'cards')=>void}>((set)=>({viewMode:'table',setViewMode:(mode)=>set({viewMode:mode})}))
