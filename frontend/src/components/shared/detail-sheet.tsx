"use client"

import * as React from "react"
import Link from "next/link"
import { ExternalLink } from "lucide-react"

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

export interface DetailSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  deepLink?: string;
  children: React.ReactNode;
}

export function DetailSheet({ isOpen, onClose, title, deepLink, children }: DetailSheetProps) {
  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:!w-[33.33vw] sm:!max-w-none bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-2xl">
        <SheetHeader className="sr-only">
          <SheetTitle>{title}</SheetTitle>
        </SheetHeader>
        
        {isOpen && (
          <div className="flex flex-col h-full mt-8">
            <div className="px-6 pt-2 pb-4">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-bold text-foreground tracking-tight">{title}</h3>
                {deepLink && (
                  <Link 
                    href={deepLink}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-blue bg-brand-blue/10 hover:bg-brand-blue/20 px-3 py-1.5 rounded-md transition-colors"
                  >
                    Open Page <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            </div>
            <div className="flex-1 flex flex-col">
              {children}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
