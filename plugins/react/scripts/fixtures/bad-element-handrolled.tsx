// RC-STRUCT-04: hand-rolled HTML attribute surface — should instead extend the
// canonical element-props helper from react. The fixture deliberately omits any
// such import — that is part of the heuristic.
export type ButtonProps = {
  onClick?: (event: unknown) => void;
  disabled?: boolean;
  type?: 'button' | 'submit';
  className?: string;
  'aria-label'?: string;
};

export const Button = (props: ButtonProps) => <button {...props} />;
