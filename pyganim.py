import pygame, time

PLAYING = 'playing'
PAUSED = 'paused'
STOPPED = 'stopped'

NORTHWEST = 'northwest'
NORTH = 'north'
NORTHEAST = 'northeast'
WEST = 'west'
CENTER = 'center'
EAST = 'east'
SOUTHWEST = 'southwest'
SOUTH = 'south'
SOUTHEAST = 'southeast'


class PygAnimation(object):
    def __init__(self, frames, loop=True):
        self._images = []
        # _durations - длительность кадра в секундах
        # например [1, 1, 2.5] означает, что первый и второй кадры длятся,
        # 1 секунду, и третий - 2.5 секунды
        self._durations = []
        self._startTimes = None

        # если спрайт изменён, то оригинал будет храниться в _images
        # а измен1нные в _transformedImages.
        self._transformedImages = []

        self._state = STOPPED # PLAYING, PAUSED или STOPPED
        self._loop = loop # если True, анимация продолжится. Если False, анимация остановится
        self._rate = 1.0 # 2.0 - анимация проигрывается в 2 раза быстрее, 0.5 - в 2 раза медленнее
        self._visibility = True # Если False, ничего не рисуется когда blit() вызван

        self._playingStartTime = 0 # время, когда play() была вызвана последний раз
        self._pausedStartTime = 0 # когда pause() была вызвана последний раз

        if frames != '_copy':
            self.numFrames = len(frames)
            for i in range(self.numFrames):
                # загружает каждый кадр анимации в _images
                frame = frames[i]
                if type(frame[0]) == str:
                    frame = (pygame.image.load(frame[0]), frame[1])
                self._images.append(frame[0])
                self._durations.append(frame[1])
            self._startTimes = self._getStartTimes()


    def _getStartTimes(self):
        startTimes = [0]
        for i in range(self.numFrames):
            startTimes.append(startTimes[-1] + self._durations[i])
        return startTimes


    def reverse(self):
        # переворячивает порядок анимаций
        self.elapsed = self._startTimes[-1] - self.elapsed
        self._images.reverse()
        self._transformedImages.reverse()
        self._durations.reverse()


    def getCopy(self):
        return self.getCopies(1)[0]


    def getCopies(self, numCopies=1):
        retval = []
        for i in range(numCopies):
            newAnim = PygAnimation('_copy', loop=self.loop)
            newAnim._images = self._images[:]
            newAnim._transformedImages = self._transformedImages[:]
            newAnim._durations = self._durations[:]
            newAnim._startTimes = self._startTimes[:]
            newAnim.numFrames = self.numFrames
            retval.append(newAnim)
        return retval


    def blit(self, destSurface, dest):
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, self.elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)


    def getFrame(self, frameNum):
        # возвращает объект pygame.Surface frameNum-ого кадра в этом
        # анимационном объекте. Если здесь трансформировааная ферсия кадра,
        # функция вернёт её.
        if self._transformedImages == []:
            return self._images[frameNum]
        else:
            return self._transformedImages[frameNum]


    def getCurrentFrame(self):
        # Возвращает объект pygame.Surface кадра, который будет нарисован
        # если blit() метод вызван в этот момент. Если здесь 3
        # трансформированная версия кадра, функция вернёт её.
        return self.getFrame(self.currentFrameNum)


    def clearTransforms(self):
        # Удаляет все трансформированные кадры так, что объект анимации
        # отображает исходные поверхности/картинки, какими они были до
        # фунций трансформаций
        # transformation functions were called on them.
        #
        # Это удобно сделать для множественного преобразования, где 
        # вызов функций перемещения или масштабирования несколько раз 
        # приводит к ухудшению/шуму изображений.
        self._transformedImages = []

    def makeTransformsPermanent(self):
        self._images = [pygame.Surface(surfObj.get_size(), 0, surfObj) for surfObj in self._transformedImages]
        for i in range(len(self._transformedImages)):
            self._images[i].blit(self._transformedImages[i], (0,0))

    def blitFrameNum(self, frameNum, destSurface, dest):
        # Рисует указанный кадр объекта анимации. 
        # Это игнорирует текущее состояние воспроизведения.
        #
        # Примечание: если атрибут видимость имеет значение false, то ничего не будет нарисовано.
        #
        # @param frameNum
        #     кадр для прорисовки (первый кадр имеет №0)
        # @param destSurface
        #     Объект Surface для прорисовки кадра
        # @param dest
        #     Позиция  для прорисовки кадра.
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        destSurface.blit(self.getFrame(frameNum), dest)


    def blitFrameAtTime(self, elapsed, destSurface, dest):
        # Рисует кадр "прошедшее" количество секунд в анимации, а не время,
        # когда анимация фактически начала играть.
        #
        # Примечание: если атрибут видимость имеет значение false, то ничего не будет нарисовано.
        #
        # @param elapsed
        #     Количество времени в анимации для использования при определении, какой кадр рисовать.
        #     blitFrameAtTime() использует этот параметр, а не фактическое время начала 
        #     воспроизведения анимации. (В секундах)
        # @param destSurface
        #     Объект Surface для прорисовки кадра
        # @param dest
        #     Позиция  для прорисовки кадра.
        if self.isFinished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frameNum = findStartTime(self._startTimes, elapsed)
        destSurface.blit(self.getFrame(frameNum), dest)


    def isFinished(self):
        # Возвращает True, если анимация закончила показ всех кадров, которые у нее есть.
        return not self.loop and self.elapsed >= self._startTimes[-1]


    def play(self, startTime=None):
        # Начинает проигрывать авнимацию

        # play() является по существу функцией сеттера для self._state

        if startTime is None:
            startTime = time.time()

        if self._state == PLAYING:
            if self.isFinished():
                # если анимация закончила показ всех кадров, то
                # вызов play() заставляет её воспроизводиться с самого начала.
                self._playingStartTime = startTime
        elif self._state == STOPPED:
            # если анимация остановлена, начинает воспроизведение с самого начала
            self._playingStartTime = startTime
        elif self._state == PAUSED:
            # если анимация была приостановлена, начинает воспроизведение с того места,
            # где она была приостановлена
            self._playingStartTime = startTime - (self._pausedStartTime - self._playingStartTime)
        self._state = PLAYING


    def pause(self, startTime=None):
        # Останавливает выполнение анимации и оставляет ее на текущем кадре.
        # pause() является по существу функцией сеттера для self._state
        if startTime is None:
            startTime = time.time()

        if self._state == PAUSED:
            return # do nothing
        elif self._state == PLAYING:
            self._pausedStartTime = startTime
        elif self._state == STOPPED:
            rightNow = time.time()
            self._playingStartTime = rightNow
            self._pausedStartTime = rightNow
        self._state = PAUSED


    def stop(self):
        # Сбрасывает анимации в начале кадра и не продолжает проигрывать
        # stop() является по существу функцией сеттера для self._state
        if self._state == STOPPED:
            return # ничего не делать
        self._state = STOPPED


    def togglePause(self):
        # Если пауза, начинает воспроизведение. Если воспроизведение, то пауза.

        # togglePause() является по существу функцией сеттера для self._state
        if self._state == PLAYING:
            if self.isFinished():
                # единственное исключение: если эта анимация не зацикливается,
                # и она закончила воспроизведение, то переключение паузы
                #приведет к воспроизведению анимации с самого начала.
                self.play()
            else:
                self.pause()
        elif self._state in (PAUSED, STOPPED):
            self.play()


    def areFramesSameSize(self):
        # Returns True если все объекты Surface в этом анимационном объекте
        # имеют одинаковую ширину и высоту. В противном случае возвращает False
        width, height = self.getFrame(0).get_size()
        for i in range(len(self._images)):
            if self.getFrame(i).get_size() != (width, height):
                return False
        return True


    def getMaxSize(self):
        frameWidths = []
        frameHeights = []
        for i in range(len(self._images)):
            frameWidth, frameHeight = self._images[i].get_size()
            frameWidths.append(frameWidth)
            frameHeights.append(frameHeight)
        maxWidth = max(frameWidths)
        maxHeight = max(frameHeights)

        return (maxWidth, maxHeight)


    def getRect(self):
        maxWidth, maxHeight = self.getMaxSize()
        return pygame.Rect(0, 0, maxWidth, maxHeight)


    def anchor(self, anchorPoint=NORTHWEST):
        if self.areFramesSameSize():
            return
        self.clearTransforms()

        maxWidth, maxHeight = self.getMaxSize()
        halfMaxWidth = int(maxWidth / 2)
        halfMaxHeight = int(maxHeight / 2)

        for i in range(len(self._images)):
            newSurf = pygame.Surface((maxWidth, maxHeight))
            newSurf = newSurf.convert_alpha()
            newSurf.fill((0,0,0,0))

            frameWidth, frameHeight = self._images[i].get_size()
            halfFrameWidth = int(frameWidth / 2)
            halfFrameHeight = int(frameHeight / 2)

            # position the Surface objects to the specified anchor point
            if anchorPoint == NORTHWEST:
                newSurf.blit(self._images[i], (0, 0))
            elif anchorPoint == NORTH:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, 0))
            elif anchorPoint == NORTHEAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, 0))
            elif anchorPoint == WEST:
                newSurf.blit(self._images[i], (0, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == CENTER:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == EAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, halfMaxHeight - halfFrameHeight))
            elif anchorPoint == SOUTHWEST:
                newSurf.blit(self._images[i], (0, maxHeight - frameHeight))
            elif anchorPoint == SOUTH:
                newSurf.blit(self._images[i], (halfMaxWidth - halfFrameWidth, maxHeight - frameHeight))
            elif anchorPoint == SOUTHEAST:
                newSurf.blit(self._images[i], (maxWidth - frameWidth, maxHeight - frameHeight))
            self._images[i] = newSurf


    def nextFrame(self, jump=1):
        self.currentFrameNum += int(jump)


    def prevFrame(self, jump=1):
        self.currentFrameNum -= int(jump)


    def rewind(self, seconds=None):
        if seconds is None:
            self.elapsed = 0.0
        else:
            self.elapsed -= seconds


    def fastForward(self, seconds=None):
        # Set the elapsed time forward relative to the current elapsed time.
        if seconds is None:
            self.elapsed = self._startTimes[-1] - 0.00002 # done to compensate for rounding errors
        else:
            self.elapsed += seconds

    def _makeTransformedSurfacesIfNeeded(self):
        # Internal-method. Creates the Surface objects for the _transformedImages list.
        # Don't call this method.
        if self._transformedImages == []:
            self._transformedImages = [surf.copy() for surf in self._images]


    # Transformation methods.
    # (These are analogous to the pygame.transform.* functions, except they
    # are applied to all frames of the animation object.
    def flip(self, xbool, ybool):
        # Flips the image horizontally, vertically, or both.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.flip
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.flip(self.getFrame(i), xbool, ybool)


    def scale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Increases or decreases the size of the images.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale(self.getFrame(i), width_height)


    def rotate(self, angle):
        # Rotates the image.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotate
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotate(self.getFrame(i), angle)


    def rotozoom(self, angle, scale):
        # Rotates and scales the image simultaneously.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotozoom
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.rotozoom(self.getFrame(i), angle, scale)


    def scale2x(self):
        # NOTE: Does not support the DestSurface parameter
        # Double the size of the image using an efficient algorithm.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale2x
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.scale2x(self.getFrame(i))


    def smoothscale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Scales the image smoothly. (Computationally more expensive and
        # slower but produces a better scaled image.)
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.smoothscale
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            self._transformedImages[i] = pygame.transform.smoothscale(self.getFrame(i), width_height)



    # pygame.Surface method wrappers
    # These wrappers call their analogous pygame.Surface methods on all Surface objects in this animation.
    # They are here for the convenience of the module user. These calls will apply to the transform images,
    # and can have their effects undone by called clearTransforms()
    #
    # It is not advisable to call these methods on the individual Surface objects in self._images.
    def _surfaceMethodWrapper(self, wrappedMethodName, *args, **kwargs):
        self._makeTransformedSurfacesIfNeeded()
        for i in range(len(self._images)):
            methodToCall = getattr(self._transformedImages[i], wrappedMethodName)
            methodToCall(*args, **kwargs)

    # There's probably a more terse way to generate the following methods,
    # but I don't want to make the code even more unreadable.
    def convert(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.convert
        self._surfaceMethodWrapper('convert', *args, **kwargs)


    def convert_alpha(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.convert_alpha
        self._surfaceMethodWrapper('convert_alpha', *args, **kwargs)


    def set_alpha(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.set_alpha
        self._surfaceMethodWrapper('set_alpha', *args, **kwargs)


    def scroll(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.scroll
        self._surfaceMethodWrapper('scroll', *args, **kwargs)


    def set_clip(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.set_clip
        self._surfaceMethodWrapper('set_clip', *args, **kwargs)


    def set_colorkey(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.set_colorkey
        self._surfaceMethodWrapper('set_colorkey', *args, **kwargs)


    def lock(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.unlock
        self._surfaceMethodWrapper('lock', *args, **kwargs)


    def unlock(self, *args, **kwargs):
        # http://pygame.org/docs/ref/surface.html#Surface.lock
        self._surfaceMethodWrapper('unlock', *args, **kwargs)



    # Getter and setter methods for properties
    def _propGetRate(self):
        return self._rate

    def _propSetRate(self, rate):
        rate = float(rate)
        if rate < 0:
            raise ValueError('rate must be greater than 0.')
        self._rate = rate

    rate = property(_propGetRate, _propSetRate)


    def _propGetLoop(self):
        return self._loop

    def _propSetLoop(self, loop):
        if self.state == PLAYING and self._loop and not loop:
            # if we are turning off looping while the animation is playing,
            # we need to modify the _playingStartTime so that the rest of
            # the animation will play, and then stop. (Otherwise, the
            # animation will immediately stop playing if it has already looped.)
            self._playingStartTime = time.time() - self.elapsed
        self._loop = bool(loop)

    loop = property(_propGetLoop, _propSetLoop)


    def _propGetState(self):
        if self.isFinished():
            self._state = STOPPED # if finished playing, then set state to STOPPED.

        return self._state

    def _propSetState(self, state):
        if state not in (PLAYING, PAUSED, STOPPED):
            raise ValueError('state должен быть одним из pyganim.PLAYING, pyganim.PAUSED, или pyganim.STOPPED')
        if state == PLAYING:
            self.play()
        elif state == PAUSED:
            self.pause()
        elif state == STOPPED:
            self.stop()

    state = property(_propGetState, _propSetState)


    def _propGetVisibility(self):
        return self._visibility

    def _propSetVisibility(self, visibility):
        self._visibility = bool(visibility)

    visibility = property(_propGetVisibility, _propSetVisibility)


    def _propSetElapsed(self, elapsed):
        # Примечание: приминительно к ошибкам округления с плавающей запятой, это не работает точно.
        elapsed += 0.00001 # done to compensate for rounding errors
        # TODO - I really need to find a better way to handle the floating point thing.

        # Set the elapsed time to a specific value.
        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getInBetweenValue(0, elapsed, self._startTimes[-1])

        rightNow = time.time()
        self._playingStartTime = rightNow - (elapsed * self.rate)

        if self.state in (PAUSED, STOPPED):
            self.state = PAUSED # если STOPPED, то сделать PAUSED
            self._pausedStartTime = rightNow


    def _propGetElapsed(self):
        # Примечание: приминительно к ошибкам округления с плавающей запятой, это не работает точно.
        if self._state == STOPPED:
            return 0

        if self._state == PLAYING:
            # при воспроизведении рисует текущий кадр (в зависимости от времени 
            # начала воспроизведения анимации). Если нет цикла и анимация уже 
            # прошла все кадры, то рисует последний кадр.
            elapsed = (time.time() - self._playingStartTime) * self.rate
        elif self._state == PAUSED:
            # если пауза, то нарисует кадр, который играл во время, когда
            # объект PygAnimation был поставлен на паузу
            elapsed = (self._pausedStartTime - self._playingStartTime) * self.rate
        if self._loop:
            elapsed = elapsed % self._startTimes[-1]
        else:
            elapsed = getInBetweenValue(0, elapsed, self._startTimes[-1])
        elapsed += 0.00001 # сделано для компенсации ошибок округления
        return elapsed

    elapsed = property(_propGetElapsed, _propSetElapsed)


    def _propGetCurrentFrameNum(self):
        # Возвращает номер кадра, который будет отображаться в данный момент,
        # если анимационный объект был нарисован прямо сейчас.
        return findStartTime(self._startTimes, self.elapsed)


    def _propSetCurrentFrameNum(self, frameNum):
        # Изменяет затраченное время на начало определенного кадра.
        if self.loop:
            frameNum = frameNum % len(self._images)
        else:
            frameNum = getInBetweenValue(0, frameNum, len(self._images)-1)
        self.elapsed = self._startTimes[frameNum]

    currentFrameNum = property(_propGetCurrentFrameNum, _propSetCurrentFrameNum)



class PygConductor(object):
    def __init__(self, *animations):
        assert len(animations) > 0, 'как минимум 1 объект PygAnimation требуется'

        self._animations = []
        self.add(*animations)


    def add(self, *animations):
        if type(animations[0]) == dict:
            for k in animations[0].keys():
                self._animations.append(animations[0][k])
        elif type(animations[0]) in (tuple, list):
            for i in range(len(animations[0])):
                self._animations.append(animations[0][i])
        else:
            for i in range(len(animations)):
                self._animations.append(animations[i])

    def _propGetAnimations(self):
        return self._animations

    def _propSetAnimations(self, val):
        self._animations = val

    animations = property(_propGetAnimations, _propSetAnimations)

    def play(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.play(startTime)

    def pause(self, startTime=None):
        if startTime is None:
            startTime = time.time()

        for animObj in self._animations:
            animObj.pause(startTime)

    def stop(self):
        for animObj in self._animations:
            animObj.stop()

    def reverse(self):
        for animObj in self._animations:
            animObj.reverse()

    def clearTransforms(self):
        for animObj in self._animations:
            animObj.clearTransforms()

    def makeTransformsPermanent(self):
        for animObj in self._animations:
            animObj.makeTransformsPermanent()

    def togglePause(self):
        for animObj in self._animations:
            animObj.togglePause()

    def nextFrame(self, jump=1):
        for animObj in self._animations:
            animObj.nextFrame(jump)

    def prevFrame(self, jump=1):
        for animObj in self._animations:
            animObj.prevFrame(jump)

    def rewind(self, seconds=None):
        for animObj in self._animations:
            animObj.rewind(seconds)

    def fastForward(self, seconds=None):
        for animObj in self._animations:
            animObj.fastForward(seconds)

    def flip(self, xbool, ybool):
        for animObj in self._animations:
            animObj.flip(xbool, ybool)

    def scale(self, width_height):
        for animObj in self._animations:
            animObj.scale(width_height)

    def rotate(self, angle):
        for animObj in self._animations:
            animObj.rotate(angle)

    def rotozoom(self, angle, scale):
        for animObj in self._animations:
            animObj.rotozoom(angle, scale)

    def scale2x(self):
        for animObj in self._animations:
            animObj.scale2x()

    def smoothscale(self, width_height):
        for animObj in self._animations:
            animObj.smoothscale(width_height)

    def convert(self):
        for animObj in self._animations:
            animObj.convert()

    def convert_alpha(self):
        for animObj in self._animations:
            animObj.convert_alpha()

    def set_alpha(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_alpha(*args, **kwargs)

    def scroll(self, dx=0, dy=0):
        for animObj in self._animations:
            animObj.scroll(dx, dy)

    def set_clip(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_clip(*args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        for animObj in self._animations:
            animObj.set_colorkey(*args, **kwargs)

    def lock(self):
        for animObj in self._animations:
            animObj.lock()

    def unlock(self):
        for animObj in self._animations:
            animObj.unlock()


def getInBetweenValue(lowerBound, value, upperBound):
    # Возвращает значение в пределах нижней и верхней границ параметров.
    # Если значение меньше чем lowerBound, тогда возвращает lowerBound.
    # Если значение больше чем upperBound, тогда возвращает upperBound.
    # В противном случае просто возвращает значение как есть.
    if value < lowerBound:
        return lowerBound
    elif value > upperBound:
        return upperBound
    return value


def findStartTime(startTimes, target):
    # С startTimes как список последовательных чисел и цели как число,
    # возвращает индекс в startTimes, который предшествует цели.
    assert startTimes[0] == 0
    lb = 0 # "lb" нижняя граница
    ub = len(startTimes) - 1 # "ub" верхняя граница

    # особые случаи:
    if len(startTimes) == 0:
        return 0
    if target >= startTimes[-1]:
        return ub - 1

    # выполнить двоичный поиск:
    while True:
        i = int((ub - lb) / 2) + lb

        if startTimes[i] == target or (startTimes[i] < target and startTimes[i+1] > target):
            if i == len(startTimes):
                return i - 1
            else:
                return i

        if startTimes[i] < target:
            lb = i
        elif startTimes[i] > target:
            ub = i
