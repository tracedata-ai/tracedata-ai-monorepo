import { useEffect, type RefObject } from "react";

export function usePageAnimations(
  containerRef: RefObject<HTMLElement | null>,
  selector = ".animate-card",
) {
  useEffect(() => {
    let cleanup: (() => void) | undefined;

    async function init() {
      const { gsap } = await import("gsap");
      const { ScrollTrigger } = await import("gsap/ScrollTrigger");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      gsap.registerPlugin(ScrollTrigger as any);

      if (!containerRef.current) return;

      const ctx = gsap.context(() => {
        gsap.from(containerRef.current, {
          opacity: 0,
          y: 16,
          duration: 0.6,
          ease: "power2.out",
        });

        const cards = containerRef.current!.querySelectorAll(selector);
        if (cards.length > 0) {
          gsap.from(cards, {
            scrollTrigger: {
              trigger: containerRef.current,
              start: "top 85%",
            },
            opacity: 0,
            y: 24,
            stagger: 0.08,
            duration: 0.5,
            ease: "power2.out",
          });
        }
      }, containerRef);

      cleanup = () => ctx.revert();
    }

    init();

    return () => {
      cleanup?.();
    };
  }, [containerRef, selector]);
}
