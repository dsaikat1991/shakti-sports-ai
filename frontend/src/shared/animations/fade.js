export const fadeUp = {
  hidden: {
    opacity: 0,
    y: 32,
  },
  visible: {
    opacity: 1,
    y: 0,
  },
};

export const fadeLeft = {
  hidden: {
    opacity: 0,
    x: 48,
  },
  visible: {
    opacity: 1,
    x: 0,
  },
};

export const fadeRight = {
  hidden: {
    opacity: 0,
    x: -48,
  },
  visible: {
    opacity: 1,
    x: 0,
  },
};

export const staggerContainer = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.12,
    },
  },
};