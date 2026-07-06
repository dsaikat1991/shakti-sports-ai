import Badge from "../../../components/ui/Badge";
import Button from "../../../components/ui/Button";
import Container from "../../../components/ui/Container";
import HeroStats from "./HeroStats";
import PoseAnalysisCard from "./PoseAnalysisCard";

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-white py-20 lg:py-24">
      <Container>
        <div className="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <Badge>Built for the road to LA 2028</Badge>

            <h1 className="mt-7 max-w-4xl font-['Anton'] text-5xl uppercase leading-[0.98] tracking-tight text-gray-950 md:text-7xl">
              Every district
              <br />
              has a champion.
              <br />
              <span className="text-orange-500">Help us find them.</span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-gray-600">
              Record a sprint, hurdles, long jump, or high jump clip on your
              phone. Shakti Sports AI reads posture, stride, speed, timing, and
              movement quality frame by frame — helping athletes improve and
              coaches discover talent faster.
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Button>Upload your first clip</Button>
              <Button variant="outline">Browse athletes as a scout</Button>
            </div>

            <HeroStats />
          </div>

          <PoseAnalysisCard />
        </div>
      </Container>
    </section>
  );
}