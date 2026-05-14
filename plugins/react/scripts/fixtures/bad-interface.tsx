// RC-STRUCT-02: should be `type CardProps = { ... }` instead of `interface`
export interface CardProps {
  title: string;
  subtitle?: string;
}

export const Card = (props: CardProps) => <div>{props.title}</div>;
