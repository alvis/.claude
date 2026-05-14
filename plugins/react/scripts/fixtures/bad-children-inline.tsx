import type { ReactNode } from 'react';

// RC-STRUCT-03: candidate for PropsWithChildren<{ accent?: string }>
export type PanelProps = {
  accent?: string;
  children: ReactNode;
};

export const Panel = (props: PanelProps) => <section>{props.children}</section>;
