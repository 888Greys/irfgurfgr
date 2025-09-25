"use client";
import { Button } from "../ui/button";
import { Sparkles, BarChart3, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

export function HeroSection() {
  const router = useRouter();
  return (
    <section className="w-full min-h-[60vh] flex flex-col items-center justify-center py-20 bg-background">
      <motion.div
        className="max-w-2xl text-center"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        <motion.h1
          className="text-4xl md:text-6xl font-bold tracking-tight mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.7, ease: "easeOut" }}
        >
          AI Readiness Assessment
        </motion.h1>
        <motion.p
          className="text-lg md:text-2xl text-muted-foreground mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.7, ease: "easeOut" }}
        >
          Discover your organization’s AI potential. Get actionable insights and a clear path to digital transformation.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.5, ease: "easeOut" }}
        >
          <Button
            size="lg"
            className="text-lg px-8 py-6 font-semibold shadow-lg transition-transform hover:scale-105 hover:shadow-xl"
            onClick={() => router.push("/assessment")}
          >
            Start Assessment
          </Button>
        </motion.div>
      </motion.div>
      <motion.div
        className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: {
            transition: {
              staggerChildren: 0.15,
            },
          },
        }}
      >
        <FeatureCard
          icon={<Sparkles className="w-8 h-8 text-primary" />}
          title="Modern & Insightful"
          description="Cutting-edge assessment, designed for today’s business needs."
        />
        <FeatureCard
          icon={<BarChart3 className="w-8 h-8 text-primary" />}
          title="Data-Driven Results"
          description="Visualize your strengths and opportunities with clarity."
        />
        <FeatureCard
          icon={<ShieldCheck className="w-8 h-8 text-primary" />}
          title="Secure & Private"
          description="Your data is protected with enterprise-grade security."
        />
      </motion.div>
    </section>
  );
}

import { Variants } from "framer-motion";

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: "easeOut" } },
};

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <motion.div
      className="flex flex-col items-center bg-card rounded-xl shadow-md p-6 border transition-transform hover:scale-105 hover:shadow-xl cursor-pointer"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.07, boxShadow: "0 8px 32px rgba(0,0,0,0.12)" }}
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-base text-muted-foreground">{description}</p>
    </motion.div>
  );
}
